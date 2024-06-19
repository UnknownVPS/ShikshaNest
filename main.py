# annotate_client.py
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
import socket
import threading

# Server settings
SERVER_IP = '0.0.0.0'  # Replace with your server's IP address
SERVER_PORT = 12345

class TouchEventSender(App):
    def build(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # GUI layout
        self.layout = BoxLayout(orientation='vertical')

        # Label to display touch event status
        self.status_label = Label(text='Touch events will be sent to the server.', size_hint=(1, 0.1))
        self.layout.add_widget(self.status_label)

        # Widget to capture touch events
        self.touch_widget = TouchWidget()
        self.layout.add_widget(self.touch_widget)

        # Connect button
        self.connect_button = Button(text='Connect to Server', size_hint=(1, 0.1))
        self.connect_button.bind(on_press=self.connect_to_server)
        self.layout.add_widget(self.connect_button)

        return self.layout

    def connect_to_server(self, instance):
        try:
            self.sock.connect((SERVER_IP, SERVER_PORT))
            self.status_label.text = f"Connected to server at {SERVER_IP}:{SERVER_PORT}"
        except Exception as e:
            self.status_label.text = f"Connection error: {e}"

    def send_touch_event(self, x, y):
        try:
            data = f"{x} {y}".encode('utf-8')
            self.sock.send(data)
        except Exception as e:
            self.status_label.text = f"Error sending touch event: {e}"

class TouchWidget(Widget):
    def on_touch_down(self, touch):
        app = App.get_running_app()
        app.send_touch_event(int(touch.x), int(touch.y))
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        app = App.get_running_app()
        app.send_touch_event(int(touch.x), int(touch.y))
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        app = App.get_running_app()
        app.send_touch_event(int(touch.x), int(touch.y))
        return super().on_touch_up(touch)

if __name__ == '__main__':
    TouchEventSender().run()
