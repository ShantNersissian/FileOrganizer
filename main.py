import socket
import threading
import os

import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox

class P2PApp:
    def __init__(self, master):
        self.master = master
        master.title("P2P File Sharing App")

        # File list
        self.file_list_box = tk.Listbox(master, height=10, width=50)
        self.file_list_box.pack(pady=10)

        # Share File button
        self.share_button = tk.Button(master, text="Share File", command=self.share_file)
        self.share_button.pack(pady=5)

        # Download File button
        self.download_button = tk.Button(master, text="Download File", command=self.download_file)
        self.download_button.pack(pady=5)

        # Status bar
        self.status = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        threading.Thread(target=self.start_server, daemon=True).start()
        
        # Input for Peer IP Address
        self.peer_ip_label = tk.Label(master, text="Peer IP:")
        self.peer_ip_label.pack(pady=2)
        self.peer_ip_entry = tk.Entry(master)
        self.peer_ip_entry.pack(pady=2)

        # Input for Peer Port
        self.peer_port_label = tk.Label(master, text="Peer Port:")
        self.peer_port_label.pack(pady=2)
        self.peer_port_entry = tk.Entry(master)
        self.peer_port_entry.pack(pady=2)

        # Connect to Peer button
        self.connect_button = tk.Button(master, text="Connect to Peer", command=self.initiate_connection)
        self.connect_button.pack(pady=5)

    def initiate_connection(self):
        peer_ip = self.peer_ip_entry.get()
        peer_port = self.peer_port_entry.get()

        if peer_ip and peer_port:
            try:
                peer_port = int(peer_port)
                self.connect_to_peer(peer_ip, peer_port)
                messagebox.showinfo("Connection", f"Connected to {peer_ip}:{peer_port}")
            except ValueError:
                messagebox.showerror("Error", "Invalid port number.")
            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please enter both IP and Port")

    def start_server(self):
        host = '0.0.0.0'
        port = 12345

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr} has been established.")

            # New thread to handle the client
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        # Receive the filename request
        file_request = client_socket.recv(1024).decode()

        # Check if the file is available
        if os.path.isfile(file_request):
            # Send file size first
            client_socket.send(str(os.path.getsize(file_request)).encode())

            # Then send the file in chunks
            with open(file_request, 'rb') as f:
                bytes_to_send = f.read(1024)
                while bytes_to_send:
                    client_socket.send(bytes_to_send)
                    bytes_to_send = f.read(1024)
        else:
            client_socket.send(b'File not found')

        client_socket.close()

    def share_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            # Logic to share the file goes here
            self.status.config(text=f"Selected {filename} to share")
            # Add file to the list
            self.file_list_box.insert(tk.END, filename)

    def download_file(self):
        selected = self.file_list_box.curselection()
        if selected:
            filename = self.file_list_box.get(selected[0])

            # Connect to the peer (You'll need the IP and port)
            peer_ip = 'peer_ip_here'
            peer_port = 12345
            self.connect_to_peer(peer_ip, peer_port, filename)
        else:
            messagebox.showwarning("Warning", "Please select a file to download")

    def connect_to_peer(self, peer_ip, peer_port, file_request):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_ip, peer_port))

            # Send file request
            client_socket.send(file_request.encode())

            # Receive file size
            file_size = int(client_socket.recv(1024).decode())

            # Now receive the file in chunks
            with open(f"downloaded_{file_request}", 'wb') as f:
                bytes_received = 0
                while bytes_received < file_size:
                    chunk = client_socket.recv(1024)
                    if not chunk: 
                        break  # Connection closed
                    f.write(chunk)
                    bytes_received += len(chunk)

            client_socket.close()
            messagebox.showinfo("Download", f"Downloaded {file_request}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to peer: {e}")

# Initialize Tkinter
root = tk.Tk()
app = P2PApp(root)
root.mainloop()