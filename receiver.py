import socket
import os
import sys
import hashlib

def xor_decrypt(data, key):
    # Decrypts data using XOR operation with the given key
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def receive_file(filename, key, host, port=5000):
    try:
        # Create a socket object for client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        client_socket.connect((host, port))

        # Receive the SHA-256 hash of the encryption key from the server
        expected_key_hash = client_socket.recv(32)  # SHA-256 hash size is 32 bytes
        key_hash = hashlib.sha256(key).digest()
        if key_hash != expected_key_hash:
            print("Error: Encryption key mismatch.")
            client_socket.close()
            return

        # Receive the size of the incoming file
        file_size_bytes = client_socket.recv(8)
        file_size = int.from_bytes(file_size_bytes, 'big')

        # Define the path where the file will be saved
        downloads_path = os.path.expanduser('~/Downloads')
        full_path = os.path.join(downloads_path, filename)

        # Receive and decrypt the file content, then save it
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
        # Close the client socket
        client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python receiver.py <filename> <encryption_key> <host> <port>")
        sys.exit(1)
    filename = sys.argv[1]
    key = sys.argv[2].encode()  # Convert the key to bytes
    host = sys.argv[3]
    port = int(sys.argv[4])
    receive_file(filename, key, host, port)
