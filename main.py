# main.py
import socket
import pickle
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line
from kivy.core.window import Window

# Set up the client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('server_ip_address', 65432))  # replace 'server_ip_address' with the server's IP address

class TouchInput(Widget):
    def __init__(self, **kwargs):
        super(TouchInput, self).__init__(**kwargs)
        self.touch_points = []

    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 1)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=2)
        self.touch_points.append((touch.x, touch.y))

    def on_touch_move(self, touch):
        with self.canvas:
            touch.ud['line'].points += [touch.x, touch.y]
        self.touch_points.append((touch.x, touch.y))
        if len(self.touch_points) >= 5:  # Send data more frequently
            self.send_touch()

    def on_touch_up(self, touch):
        self.send_touch()  # Send remaining points when touch ends
        self.touch_points = []

    def send_touch(self):
        if self.touch_points:
            positions = [(p[0], Window.height - p[1]) for p in self.touch_points]  # Correct coordinate inversion
            data = pickle.dumps(positions)
            client_socket.sendall(data)
            self.touch_points = []

class MyApp(App):
    def build(self):
        parent = FloatLayout()
        touch_input = TouchInput()
        parent.add_widget(touch_input)
        return parent

if __name__ == '__main__':
    MyApp().run()
    client_socket.close()
