# main.py
import socket
import pickle
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window

# Set up the client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('0.0.0.0', 65432))  # replace 'server_ip_address' with the server's IP address

class TouchInput(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 1)
            d = 30.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
        self.send_touch(touch.pos)

    def on_touch_move(self, touch):
        with self.canvas:
            Color(1, 1, 1)
            d = 30.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
        self.send_touch(touch.pos)

    def send_touch(self, pos):
        data = pickle.dumps([pos])
        client_socket.sendall(data)

class MyApp(App):
    def build(self):
        parent = FloatLayout()
        touch_input = TouchInput()
        parent.add_widget(touch_input)
        return parent

if __name__ == '__main__':
    MyApp().run()
    client_socket.close()
