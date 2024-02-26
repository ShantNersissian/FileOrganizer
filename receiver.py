import socket
import os

def receive_file(filename, host, port=5000):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        downloads_path = os.path.expanduser('~/Downloads')  # Works on both Windows and Unix-like systems
        full_path = os.path.join(downloads_path, filename)

        with open(full_path, 'wb') as file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
        print(f"File {filename} received and saved to Downloads folder.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    host = input("Enter the server's IP address: ")
    port = int(input("Enter the port number (default is 5000): ") or 5000)
    filename = input("Enter the desired filename for the saved file: ")
    receive_file(filename, host, port)
