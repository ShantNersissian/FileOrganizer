import sys, socket, os, hashlib
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

DARK_THEME_STYLESHEET = """
QWidget {
    background-color: #2D2D2D;
    color: #E0E0E0;
    font-family: 'Segoe UI';
    font-size: 14px;
}

QLineEdit {
    border: 2px solid #555555;
    border-radius: 5px;
    padding: 5px;
    background-color: #333333;
    color: #E0E0E0;
}

QPushButton {
    border: 2px solid #555555;
    border-radius: 5px;
    padding: 5px;
    background-color: #555555;
    color: #E0E0E0;
}

QPushButton:hover {
    background-color: #777777;
}

QLabel {
    color: #E0E0E0;
}
"""

def xor_decrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def receive_file(key, host='localhost', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, port))
            
            expected_key_hash = client_socket.recv(32)
            key_hash = hashlib.sha256(key).digest()
            if key_hash != expected_key_hash:
                print("Error: Encryption key mismatch.")
                return

            file_name_length = int.from_bytes(client_socket.recv(4), 'big')
            file_name = client_socket.recv(file_name_length).decode()

            file_size = int.from_bytes(client_socket.recv(8), 'big')
            downloads_path = os.path.expanduser('~/Downloads')
            full_path = os.path.join(downloads_path, file_name)

            received_data = b''
            while len(received_data) < file_size:
                data = client_socket.recv(1024)
                if not data:
                    break
                received_data += data

            decrypted_data = xor_decrypt(received_data, key)
            with open(full_path, 'wb') as file:
                file.write(decrypted_data)

            # Receive the SHA-256 hash from the sender
            received_file_hash = client_socket.recv(32)

            # Calculate the hash of the decrypted data
            local_file_hash = hashlib.sha256(decrypted_data).digest()

            if received_file_hash != local_file_hash:
                print("Error: File integrity check failed, the file may be corrupted.")
            else:
                print(f"\nFile {file_name} received and integrity check passed.")
        except Exception as e:
            print(f"An error occurred: {e}")

class ReceiverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Receiver")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet(DARK_THEME_STYLESHEET)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Enter encryption key")
        self.host_edit = QLineEdit("localhost")
        self.port_edit = QLineEdit("5000")
        self.start_button = QPushButton("Start Receiving")
        
        layout.addWidget(QLabel("Encryption Key:"))
        layout.addWidget(self.key_edit)
        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_edit)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_edit)
        layout.addWidget(self.start_button)
        
        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_receiving)

    def start_receiving(self):
        key_text = self.key_edit.text()
        if not key_text.strip():
            print("Encryption key cannot be empty. Please enter a valid key.")
            return
        key = key_text.encode()
        host = self.host_edit.text()
        port = int(self.port_edit.text())
        receive_file(key, host, port)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReceiverWindow()
    window.show()
    sys.exit(app.exec())
