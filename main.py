from tkinter import *
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk
import socket
import threading
import hashlib

root = Tk()
root.title("P2P File Sharing")
root.geometry("450x560+500+200")
root.configure(bg="#f4fdfe")
root.resizable(False, False)

def resize_image(image_path, new_width, new_height):
    original_image = Image.open(image_path)
    resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized_image)

def send_file(filename, host, port):
    try:
        # Get the size of the file
        filesize = os.path.getsize(filename)
        # Open the file
        with open(filename, 'rb') as file:
            # Create a checksum object
            checksum = hashlib.md5()
            
            # Read the file and update the checksum
            data = file.read()
            checksum.update(data)
            
        # Connect to the receiver
        s = socket.socket()
        s.connect((host, int(port)))
        
        # Send the file size and checksum first
        s.sendall(f"{filesize}|{checksum.hexdigest()}".encode())
        
        # Wait for the receiver to acknowledge the file size and checksum
        s.recv(1024)
        
        # Reopen the file and send the data
        with open(filename, 'rb') as file:
            s.sendfile(file)
        
        messagebox.showinfo("Success", "File sent successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send file: {e}")
    finally:
        # Shutdown and close the socket
        s.shutdown(socket.SHUT_WR)
        s.close()

def receive_file(save_path, port):
    try:
        # Create a socket and listen for a connection
        s = socket.socket()
        s.bind(('', int(port)))
        s.listen(1)
        conn, addr = s.accept()

        # Receive the file size and checksum
        received = conn.recv(1024).decode()
        filesize, sent_checksum = received.split('|')
        filesize = int(filesize)
        
        # Acknowledge the file size and checksum
        conn.sendall(b"ACK")
        
        # Receive the file data
        with open(save_path, 'wb') as file:
            bytes_received = 0
            checksum = hashlib.md5()
            while bytes_received < filesize:
                data = conn.recv(4096)
                file.write(data)
                checksum.update(data)
                bytes_received += len(data)

        # Verify the checksum
        if checksum.hexdigest() == sent_checksum:
            messagebox.showinfo("Success", "File received successfully.")
        else:
            messagebox.showerror("Error", "File corrupted during transfer.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to receive file: {e}")
    finally:
        # Close the connection and the listening socket
        conn.close()
        s.close()

def send_window():
    window = Toplevel(root)
    window.title("Send File")
    window.geometry('450x250+500+200')
    window.configure(bg="#f4fdfe")
    window.resizable(False, False)

    Label(window, text="File Path:", bg="#f4fdfe").grid(row=0, column=0, padx=10, pady=10)
    file_path_entry = Entry(window, width=50)
    file_path_entry.grid(row=0, column=1, padx=10, pady=10)

    Label(window, text="Host:", bg="#f4fdfe").grid(row=1, column=0)
    host_entry = Entry(window, width=50)
    host_entry.grid(row=1, column=1, padx=10, pady=10)

    Label(window, text="Port:", bg="#f4fdfe").grid(row=2, column=0)
    port_entry = Entry(window, width=50)
    port_entry.grid(row=2, column=1, padx=10, pady=10)

    def browse_file():
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select File')
        file_path_entry.delete(0, END)
        file_path_entry.insert(0, file_path)

    def send_action():
        threading.Thread(target=send_file, args=(file_path_entry.get(), host_entry.get(), port_entry.get())).start()

    Button(window, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)
    Button(window, text="Send", command=send_action).grid(row=3, column=1, padx=10, pady=10)

def receive_window():
    window = Toplevel(root)
    window.title("Receive File")
    window.geometry('450x150+500+200')
    window.configure(bg="#f4fdfe")
    window.resizable(False, False)

    Label(window, text="Save Path:", bg="#f4fdfe").grid(row=0, column=0, padx=10, pady=10)
    save_path_entry = Entry(window, width=50)
    save_path_entry.grid(row=0, column=1, padx=10, pady=10)

    Label(window, text="Port:", bg="#f4fdfe").grid(row=1, column=0)
    port_entry = Entry(window, width=50)
    port_entry.grid(row=1, column=1, padx=10, pady=10)

    def receive_action():
        threading.Thread(target=receive_file, args=(save_path_entry.get(), port_entry.get())).start()

    Button(window, text="Receive", command=receive_action).grid(row=2, column=1, padx=10, pady=10)

send_btn = Button(root, text="Send File", command=send_window, width=20, height=2)
send_btn.place(x=50, y=100)

receive_btn = Button(root, text="Receive File", command=receive_window, width=20, height=2)
receive_btn.place(x=250, y=100)

root.mainloop()