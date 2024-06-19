#!/usr/bin/env python3
import tkinter as tk
import socket
import threading

# Global variables for screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = (1366, 768)  # Adjust as per your screen resolution

# Colors
DRAW_COLOR = 'black'

class ScreenAnnotatorServer:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg='white')
        self.canvas.pack()

        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()

    def draw_circle(self, x, y):
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=DRAW_COLOR, outline=DRAW_COLOR)

    def start_server(self):
        # Initialize socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 12345))  # Bind to all interfaces on port 12345
        server_socket.listen(1)  # Listen for incoming connections

        print("Server is listening for connections...")
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                x, y = map(int, data.split())
                self.draw_circle(x, y)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

        client_socket.close()
        print("Connection closed.")

def main():
    root = tk.Tk()
    root.title("Screen Annotation - Server")
    app = ScreenAnnotatorServer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
