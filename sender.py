import socket
import os

def xor_encrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def send_file(filename, key, host='0.0.0.0', port=5000):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Listening on {host}:{port}")

        client_socket, address = server_socket.accept()
        print(f"Connection from {address} has been established.")

        file_size = os.path.getsize(filename)
        client_socket.sendall(file_size.to_bytes(8, 'big'))

        with open(filename, 'rb') as file:
            data = file.read(1024)
            while data:
                encrypted_data = xor_encrypt(data, key)
                client_socket.send(encrypted_data)
                data = file.read(1024)
        print(f"\nFile {filename} sent to {address}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    filename = input("Enter the path to the file you want to share: ")
    key = input("Enter the encryption key: ").encode()  # Simple string as key
    send_file(filename, key)
