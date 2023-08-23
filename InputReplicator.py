import random
import tkinter as tk
import time
import logging
import tkinter.scrolledtext as scrolledtext
from pynput.mouse import Listener as MouseListener, Controller
from pynput import mouse, keyboard

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

        #Emergency stop
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)  # Listener for keyboard events
        self.emergency_stop_flag = False

        # other initialisations...
        self.min_click_delay = 0.1  # minimum delay between clicks (in seconds)
        self.max_click_delay = 0.5  # maximum delay between clicks (in seconds)
        self.stop_replay_flag = False  # Flag to stop replay

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger()

        self.record_label = tk.Label(root, text="Press 'R' to start recording")

        self.stop_label = tk.Label(root, text="Press 'S' to stop recording")

        self.iterations_entry = tk.Entry(root)
        self.num_iterations = 1
        self.focus_label = tk.Label(root, text="")
        self.iterations_entry.bind("<Return>", self.handle_iterations_entry)
        self.iterations_entry.bind("<FocusOut>", self.remove_focus)

        self.replay_label = tk.Label(root, text="Press 'P' to replay recording")
        self.replay_button = tk.Button(root, text="Replay", command=self.replay_recorded)
        self.replay_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")


        self.record_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.stop_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.iterations_entry.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.focus_label.grid(row=3, column=0)  # Espace vide pour perdre le focus
        self.replay_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
        self.log_text.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky="e")

        self.root.bind("r", self.start_recording)
        self.root.bind("s", self.stop_recording)
        self.root.bind("p", self.start_replay)

        self.recorded_actions = []
        self.is_recording = False
        self.mouse = Controller()
        self.delay = 0.0025

        self.mouse_listener = None  # Listener for mouse events

        self.root.after(0, self.start_mouse_listener)
        self.start_keyboard_listener()

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
        self.log("Started recording")

    def stop_recording(self, event=None):
        self.is_recording = False
        self.log("Stopped recording")

    def start_replay_loop(self):
        try:
            self.num_iterations = int(self.iterations_entry.get())
        except ValueError:
            logging.error("Invalid number of iterations")

    def handle_iterations_entry(self, event):
        try:
            self.num_iterations = int(self.iterations_entry.get())
            self.remove_focus()
            self.log("Iteration set to : {} ".format(self.num_iterations))
            #self.replay_recorded()  plus bon ?
        except ValueError:
            self.log("Invalid number of iterations")
            logging.error("Invalid number of iterations")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Défilement automatique vers le bas


    def remove_focus(self, event=None):
        self.focus_label.focus_set()

    def on_mouse_move(self, x, y):
        if self.is_recording:
            self.recorded_actions.append(("move", (x, y)))
            self.log(f"Move: x={x}, y={y}")

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            if self.is_recording:
                self.recorded_actions.append(("click", (x, y, button)))
                self.log(f"Click: x={x}, y={y}, button={button}")

    def on_mouse_scroll(self, x, y, dx, dy):
        if self.is_recording:
            self.recorded_actions.append(("scroll", (x, y, dx, dy)))
            self.log(f"Scroll: x={x}, y={y}, dx={dx}, dy={dy}")

    def start_replay(self, event=None):
        self.replay_recorded()

    def replay_recorded(self, event=None):
        #self.stop_replay_flag = False  # Reset the flag
        self.emergency_stop_flag = False
        if self.num_iterations == 0:
            self.log("Infinite loop started")
            while not self.emergency_stop_flag:
                self.perform_replay(iteration=None) # None for infinite
        else:
            for i in range(self.num_iterations, 0, -1):
                if self.emergency_stop_flag:
                    break  # Stop the replay
                self.perform_replay(iteration=i)
            

    def perform_replay(self, iteration=None):
        for action, data in self.recorded_actions:
                if action == "move":
                    x, y = data
                    self.mouse.position = (x, y)
                elif action == "click":
                    x, y, button = data
                    self.mouse.position = (x, y)
                    self.random_sleep()  # wait for a more human behavior click
                    self.mouse.click(button)
                elif action == "scroll":
                    x, y, dx, dy = data
                    self.mouse.scroll(dx, dy)
                self.log(f"Replayed action: {action}, data={data}")
                if iteration is not None:
                    self.log(f"Iterations left: {iteration}")
                time.sleep(self.delay)


    def random_sleep(self):
        delay = random.uniform(self.min_click_delay, self.max_click_delay)
        time.sleep(delay)

    def start_keyboard_listener(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.esc and not self.emergency_stop_flag: # avoid double logs when escape button is released
                self.emergency_stop()
                self.log("Emergency stop")
        except AttributeError:
            pass  # Ignore non-keyboard keys

    def emergency_stop(self):
        self.emergency_stop_flag = True

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = InputReplicatorApp(root)
    app.start_keyboard_listener()
    app.run()