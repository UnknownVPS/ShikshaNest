# server.py
import socket
import pygame
import pickle
from itertools import tee

def interpolate_points(points):
    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
    
    interpolated = []
    for (x0, y0), (x1, y1) in pairwise(points):
        interpolated.append((x0, y0))
        steps = max(abs(x1 - x0), abs(y1 - y0))
        if steps == 0:
            continue
        for step in range(1, int(steps)):
            x = x0 + (x1 - x0) * step / steps
            y = y0 + (y1 - y0) * step / steps
            interpolated.append((x, y))
    interpolated.append(points[-1])
    return interpolated

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
        if len(positions) > 1:
            smoothed_positions = interpolate_points(positions)
            pygame.draw.lines(screen, (255, 255, 255), False, smoothed_positions, 5)
    except pickle.PickleError:
        continue

    pygame.display.flip()

conn.close()
server_socket.close()
pygame.quit()
