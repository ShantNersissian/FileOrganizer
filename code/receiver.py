import sys, socket, os, hashlib
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

def xor_decrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def receive_file(filename, key, host='localhost', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, port))
            
            expected_key_hash = client_socket.recv(32)
            key_hash = hashlib.sha256(key).digest()
            if key_hash != expected_key_hash:
                print("Error: Encryption key mismatch.")
                return

            file_size_bytes = client_socket.recv(8)
            file_size = int.from_bytes(file_size_bytes, 'big')
            downloads_path = os.path.expanduser('~/Downloads')
            full_path = os.path.join(downloads_path, filename)

            with open(full_path, 'wb') as file:
                total_received = 0
                while total_received < file_size:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    decrypted_data = xor_decrypt(data, key)
                    file.write(decrypted_data)
                    total_received += len(decrypted_data)
            print(f"\nFile {filename} received and saved to Downloads folder.")
        except Exception as e:
            print(f"An error occurred: {e}")

class ReceiverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Receiver")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()

        self.filename_edit = QLineEdit()
        self.key_edit = QLineEdit()
        self.host_edit = QLineEdit()
        self.port_edit = QLineEdit("5000")
        self.start_button = QPushButton("Start Receiving")

        layout.addWidget(QLabel("Filename:"))
        layout.addWidget(self.filename_edit)
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
        filename = self.filename_edit.text()
        key_text = self.key_edit.text()
        if not key_text.strip():
            print("Encryption key cannot be empty. Please enter a valid key.")
            return
        key = key_text.encode()
        host = self.host_edit.text()
        port = int(self.port_edit.text())
        receive_file(filename, key, host, port)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReceiverWindow()
    window.show()
    sys.exit(app.exec())
