import os
import sys
import socket
import hashlib
import zipfile
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

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

def decompress_file(zip_filename):
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        zipf.extractall(os.path.dirname(zip_filename))

def receive_file(key, host='localhost', port=5000):
    documents_dir = Path.home() / 'Documents' / 'ReceivedFiles'
    documents_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.bind((host, port))
            client_socket.listen(1)
            print(f"Listening on {host}:{port}")

            conn, addr = client_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                key_hash = conn.recv(32)
                if hashlib.sha256(key).digest() != key_hash:
                    print("Error: Encryption key mismatch.")
                    return

                file_name_length = int.from_bytes(conn.recv(4), 'big')
                file_name = conn.recv(file_name_length).decode()

                file_size = int.from_bytes(conn.recv(8), 'big')
                received_data = b''
                while len(received_data) < file_size:
                    data = conn.recv(1024)
                    if not data:
                        break
                    received_data += data

                decrypted_data = xor_encrypt_decrypt(received_data, key)
                zip_filename = documents_dir / ("received_" + file_name)
                with open(zip_filename, 'wb') as file:
                    file.write(decrypted_data)

                print(f"File {file_name} received and saved to {zip_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

class ReceiverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Receiver")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
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
        key = self.key_edit.text().encode()
        host = self.host_edit.text()
        port = int(self.port_edit.text())
        receive_file(key, host, port)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_STYLESHEET)
    window = ReceiverWindow()
    window.show()
    sys.exit(app.exec())