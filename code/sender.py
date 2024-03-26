import sys, socket, os, hashlib
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

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

def xor_encrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def send_file(filename, key, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"Listening on {host}:{port}")

            client_socket, address = server_socket.accept()
            with client_socket:
                print(f"Connection from {address} has been established.")

                key_hash = hashlib.sha256(key).digest()
                client_socket.sendall(key_hash)

                file_name = os.path.basename(filename).encode()
                client_socket.sendall(len(file_name).to_bytes(4, 'big'))
                client_socket.sendall(file_name)

                with open(filename, 'rb') as file:
                    file_data = file.read()

                encrypted_data = xor_encrypt(file_data, key)
                client_socket.sendall(len(encrypted_data).to_bytes(8, 'big'))
                client_socket.sendall(encrypted_data)

                # Send the SHA-256 hash of the original file data
                file_hash = hashlib.sha256(file_data).digest()
                client_socket.sendall(file_hash)

                print(f"\nFile {filename} sent to {address}")
        except Exception as e:
            print(f"An error occurred: {e}")

class SenderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Sender")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet(DARK_THEME_STYLESHEET)
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        file_layout = QHBoxLayout()
        file_layout.setSpacing(5)
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("Drag and drop or browse to select file")
        self.browse_button = QPushButton("Browse")
        
        file_layout.addWidget(self.filename_edit)
        file_layout.addWidget(self.browse_button)
        
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Enter encryption key")
        self.host_edit = QLineEdit("localhost")
        self.port_edit = QLineEdit("5000")
        self.start_button = QPushButton("Start Sending")
        
        layout.addLayout(file_layout)
        layout.addWidget(QLabel("Encryption Key:"))
        layout.addWidget(self.key_edit)
        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_edit)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_edit)
        layout.addWidget(self.start_button)
        
        self.setLayout(layout)

        self.browse_button.clicked.connect(self.browse_file)
        self.start_button.clicked.connect(self.start_sending)

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filename:
            self.filename_edit.setText(filename)

    def start_sending(self):
        filename = self.filename_edit.text()
        key_text = self.key_edit.text()
        if not key_text.strip():
            print("Encryption key cannot be empty. Please enter a valid key.")
            return
        key = key_text.encode()
        host = self.host_edit.text()
        port = int(self.port_edit.text())
        send_file(filename, key, host, port)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            self.filename_edit.setText(url.toLocalFile())
            event.acceptProposedAction()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SenderWindow()
    window.show()
    sys.exit(app.exec())
