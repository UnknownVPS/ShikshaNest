import socket
import pickle
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.uix.label import Label

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
        # Invert the y-coordinate
        inverted_pos = (pos[0], Window.height - pos[1])
        data = pickle.dumps([inverted_pos])
        self.client_socket.sendall(data)

class MyApp(App):
    def build(self):
        self.server_ip = None

        # Create layout for IP input
        self.ip_input_layout = BoxLayout(orientation='vertical')
        self.ip_input_label = Label(text="Enter the server IP address:")
        self.ip_text_input = TextInput(multiline=False)
        self.ip_submit_button = Button(text="Connect")
        self.ip_submit_button.bind(on_press=self.connect_to_server)

        self.ip_input_layout.add_widget(self.ip_input_label)
        self.ip_input_layout.add_widget(self.ip_text_input)
        self.ip_input_layout.add_widget(self.ip_submit_button)

        return self.ip_input_layout

    def connect_to_server(self, instance):
        self.server_ip = self.ip_text_input.text

        # Set up the client
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, 65432))
        except socket.error as e:
            self.ip_input_label.text = f"Connection failed: {e}"
            return

        # Switch to the main layout
        self.main_layout = FloatLayout()
        self.touch_input = TouchInput()
        self.touch_input.client_socket = self.client_socket
        self.main_layout.add_widget(self.touch_input)
        self.root.clear_widgets()
        self.root.add_widget(self.main_layout)

    def on_stop(self):
        if self.server_ip:
            self.client_socket.close()

if __name__ == '__main__':
    MyApp().run()
