import socket

def send_file(filename, host='0.0.0.0', port=5000):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Listening on {host}:{port}")

        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address} has been established.")

            with open(filename, 'rb') as file:
                data = file.read(1024)
                while data:
                    client_socket.send(data)
                    data = file.read(1024)
            print(f"File {filename} sent to {address}")
            break  # Remove this if you want to send the file to multiple clients
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    filename = input("Enter the path to the file you want to share: ")
    send_file(filename)
