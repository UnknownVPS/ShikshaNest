# main.py
import socket
import pickle
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

class TouchInput(Widget):
    def __init__(self, client_socket, **kwargs):
        super(TouchInput, self).__init__(**kwargs)
        self.client_socket = client_socket
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
            self.client_socket.sendall(data)
            self.touch_points = []

class MyApp(App):
    def build(self):
        self.client_socket = None
        return self.create_ip_prompt()

    def create_ip_prompt(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Enter Server IP Address:")
        self.text_input = TextInput(multiline=False)
        button = Button(text="Connect")
        button.bind(on_release=self.connect_to_server)
        
        layout.add_widget(label)
        layout.add_widget(self.text_input)
        layout.add_widget(button)
        
        self.popup = Popup(title='Server IP', content=layout, size_hint=(0.8, 0.5))
        self.popup.open()

    def connect_to_server(self, instance):
        server_ip = self.text_input.text
        self.popup.dismiss()
        
        # Set up the client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((server_ip, 65432))
            self.show_drawing_screen()
        except socket.error as e:
            error_popup = Popup(title='Connection Error',
                                content=Label(text=f"Failed to connect to {server_ip}\n{str(e)}"),
                                size_hint=(0.8, 0.5))
            error_popup.open()

    def show_drawing_screen(self):
        parent = FloatLayout()
        touch_input = TouchInput(client_socket=self.client_socket)
        parent.add_widget(touch_input)
        return parent

    def on_stop(self):
        if self.client_socket:
            self.client_socket.close()

if __name__ == '__main__':
    MyApp().run()
