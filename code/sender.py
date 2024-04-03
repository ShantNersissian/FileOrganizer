import sys
import socket
import os
import hashlib
import zipfile
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout

DARK_THEME_STYLESHEET = """
QWidget {
    background-color: #333;
    color: #EEE;
    font-family: 'Segoe UI';
    font-size: 14px;
}

QLineEdit {
    border: 2px solid #555;
    border-radius: 5px;
    padding: 5px;
    background-color: #444;
    color: #EEE;
}

QPushButton {
    border: 2px solid #555;
    border-radius: 5px;
    padding: 5px;
    background-color: #666;
    color: #FFF;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #777;
}

QLabel {
    color: #AAA;
}
"""

def xor_encrypt_decrypt(data, key):
    key_length = len(key)
    return bytes([data[i] ^ key[i % key_length] for i in range(len(data))])

def compress_file(original_file):
    zip_filename = original_file + '.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(original_file, os.path.basename(original_file))
    return zip_filename

def send_file(filename, key, host, port):
    compressed_filename = compress_file(filename)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect((host, port))
            print(f"Connecting to {host}:{port}")

            key_hash = hashlib.sha256(key).digest()
            server_socket.sendall(key_hash)

            file_name = os.path.basename(compressed_filename).encode()
            server_socket.sendall(len(file_name).to_bytes(4, 'big'))
            server_socket.sendall(file_name)

            with open(compressed_filename, 'rb') as file:
                file_data = file.read()

            encrypted_data = xor_encrypt_decrypt(file_data, key)
            server_socket.sendall(len(encrypted_data).to_bytes(8, 'big'))
            server_socket.sendall(encrypted_data)

            file_hash = hashlib.sha256(file_data).digest()
            server_socket.sendall(file_hash)

            print(f"File {compressed_filename} sent successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

class SenderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Sender")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        file_layout = QHBoxLayout()
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
        
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            self.filename_edit.setText(url.toLocalFile())
            event.acceptProposedAction()

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filename:
            self.filename_edit.setText(filename)

    def start_sending(self):
        filename = self.filename_edit.text()
        key = self.key_edit.text().encode()
        host = self.host_edit.text()
        port = int(self.port_edit.text())
        send_file(filename, key, host, port)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_STYLESHEET)
    window = SenderWindow()
    window.show()
    sys.exit(app.exec())