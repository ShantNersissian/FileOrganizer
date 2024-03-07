import sys, socket, os, hashlib
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

def xor_encrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def send_file(filename, key, host='0.0.0.0', port=5000):
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

                file_size = os.path.getsize(filename)
                client_socket.sendall(file_size.to_bytes(8, 'big'))

                with open(filename, 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        encrypted_data = xor_encrypt(data, key)
                        client_socket.sendall(encrypted_data)
                print(f"\nFile {filename} sent to {address}")
        except Exception as e:
            print(f"An error occurred: {e}")

class SenderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Sender")
        self.setGeometry(100, 100, 500, 300)
        self.setAcceptDrops(True)
        layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        self.filename_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        file_layout.addWidget(self.filename_edit)
        file_layout.addWidget(self.browse_button)

        self.key_edit = QLineEdit()
        self.host_edit = QLineEdit("0.0.0.0")
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
