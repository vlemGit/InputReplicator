import random
import tkinter as tk
import time
import logging
from pynput.mouse import Listener as MouseListener, Controller
from pynput import mouse

class InputReplicatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Input Replicator")

        # Define initial size of app
        self.initial_width = 600
        self.initial_height = 300
        self.root.geometry(f"{self.initial_width}x{self.initial_height}")
        
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # other initialisations...
        self.min_click_delay = 0.1  # minimum delay between clicks (in seconds)
        self.max_click_delay = 0.5  # maximum delay between clicks (in seconds)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

        self.record_label = tk.Label(root, text="Press 'R' to start recording")
        self.record_label.pack()

        self.stop_label = tk.Label(root, text="Press 'S' to stop recording")
        self.stop_label.pack()

        self.play_label = tk.Label(root, text="Press 'P' to replay recording")
        self.play_label.pack()

        self.root.bind("r", self.start_recording)
        self.root.bind("s", self.stop_recording)
        self.root.bind("p", self.replay_recorded)

        self.recorded_actions = []
        self.is_recording = False
        self.mouse = Controller()
        self.delay = 0.0025

        self.mouse_listener = None  # Listener for mouse events

        self.root.after(0, self.start_mouse_listener)

    def start_mouse_listener(self):
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click,
            on_move=self.on_mouse_move,
            on_scroll=self.on_mouse_scroll
        )
        self.mouse_listener.start()

    def start_recording(self, event=None):
        self.recorded_actions = []
        self.is_recording = True
        logging.info("Started recording")

    def stop_recording(self, event=None):
        self.is_recording = False
        logging.info("Stopped recording")

    def on_mouse_move(self, x, y):
        if self.is_recording:
            self.recorded_actions.append(("move", (x, y)))
            logging.info(f"Move: x={x}, y={y}")

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            if self.is_recording:
                self.recorded_actions.append(("click", (x, y, button)))
                logging.info(f"Click: x={x}, y={y}, button={button}")

    def on_mouse_scroll(self, x, y, dx, dy):
        if self.is_recording:
            self.recorded_actions.append(("scroll", (x, y, dx, dy)))
            logging.info(f"Scroll: x={x}, y={y}, dx={dx}, dy={dy}")

    def replay_recorded(self, event=None):
        for action, data in self.recorded_actions:
            if action == "move":
                x, y = data
                self.mouse.position = (x, y)
            elif action == "click":
                x, y, button = data
                self.mouse.position = (x, y)
                self.random_sleep()  # wait for a more humain behavior click
                self.mouse.click(button)
            elif action == "scroll":
                x, y, dx, dy = data
                self.mouse.scroll(dx, dy)
            logging.info(f"Replayed action: {action}, data={data}")
            time.sleep(self.delay)


    def random_sleep(self):
        delay = random.uniform(self.min_click_delay, self.max_click_delay)
        time.sleep(delay)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = InputReplicatorApp(root)
    app.run()