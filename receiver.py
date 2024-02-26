import socket
import os

def xor_decrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def receive_file(filename, key, host, port=5000):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

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
                total_received += len(data)
        print(f"\nFile {filename} received and saved to Downloads folder.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    host = input("Enter the server's IP address: ")
    port = int(input("Enter the port number (default is 5000): ") or 5000)
    filename = input("Enter the desired filename for the saved file: ")
    key = input("Enter the encryption key: ").encode()  # Simple string as key
    receive_file(filename, key, host, port)
