import socket
import os
import sys
import hashlib

def xor_encrypt(data, key):
    # Encrypts data using XOR operation with the given key
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key)) + key[:len(data) % len(key)]))

def send_file(filename, key, host='0.0.0.0', port=5000):
    try:
        # Create a socket object for server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the host and port
        server_socket.bind((host, port))
        # Listen for incoming connections
        server_socket.listen(1)
        print(f"Listening on {host}:{port}")

        # Accept a connection from a client
        client_socket, address = server_socket.accept()
        print(f"Connection from {address} has been established.")

        # Send SHA-256 hash of the encryption key to the client for verification
        key_hash = hashlib.sha256(key).digest()
        client_socket.sendall(key_hash)

        # Send the size of the file to be sent
        file_size = os.path.getsize(filename)
        client_socket.sendall(file_size.to_bytes(8, 'big'))

        # Open the file and send its encrypted content
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
        # Close client and server sockets
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python sender.py <filename> <encryption_key> <host> <port>")
        sys.exit(1)
    filename = sys.argv[1]
    key = sys.argv[2].encode()  # Convert the key to bytes
    host = sys.argv[3]
    port = int(sys.argv[4])
    send_file(filename, key, host, port)
