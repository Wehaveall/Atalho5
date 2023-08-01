from pynput import keyboard, mouse
from datetime import datetime
import json


class MacroFunctions:
    def __init__(self):
        self.macro = []
        self.recording = False
        self.paused = False
        self.mouse_listener = None

    def on_key_press(self, key):
        if self.recording and not self.paused:
            self.macro.append(("key_press", str(key), str(datetime.now())))

    def on_key_release(self, key):
        if self.recording and not self.paused:
            self.macro.append(("key_release", str(key), str(datetime.now())))

    def on_move(self, x, y):
        if self.recording and not self.paused:
            self.macro.append(("mouse_move", (x, y), str(datetime.now())))

    def on_click(self, x, y, button, pressed):
        if self.recording and not self.paused:
            self.macro.append(
                ("mouse_click", (x, y, str(button), pressed), str(datetime.now()))
            )

    def on_scroll(self, x, y, dx, dy):
        if self.recording and not self.paused:
            self.macro.append(("mouse_scroll", (x, y, dx, dy), str(datetime.now())))

    def start_recording(self):
        self.recording = True
        self.macro.append(("start", "", str(datetime.now())))

        self.mouse_listener = mouse.Listener(
            on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll
        )
        self.mouse_listener.start()

        return {"status": "Recording started"}  # Return a value

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.macro.append(("stop", "", str(datetime.now())))

            # Stop the mouse listener
            self.mouse_listener.stop()

        return self.macro

    def pause_recording(self):
        if self.recording:
            self.paused = True
            self.macro.append(("pause", "", str(datetime.now())))

        return self.macro

    def resume_recording(self):
        if self.paused:
            self.paused = False
            self.macro.append(("resume", "", str(datetime.now())))

        return self.macro

    def save_macro(self, filename):
        with open(filename, "w") as f:
            json.dump(self.macro, f)

        return self.macro

    def get_macro(self):
        return self.macro
