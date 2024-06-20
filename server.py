# server.py
import socket
import pygame
import pickle

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Drawing Server")
running = True

# Set up the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 65432))
server_socket.listen(1)
print("Waiting for a connection...")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    data = conn.recv(4096)
    if not data:
        break

    try:
        positions = pickle.loads(data)
        for pos in positions:
            pygame.draw.circle(screen, (255, 255, 255), pos, 5)
    except pickle.PickleError:
        continue

    pygame.display.flip()

conn.close()
server_socket.close()
pygame.quit()
