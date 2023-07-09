import webview
import threading
import time

import pygetwindow as gw
from screeninfo import get_monitors

import listener  # import listener.py
from listener import KeyListener

# Import database
from src.database.data_connect import (
    create_db,
    insert_into_db,
    get_data_from_database,
    inject_data,
)

from ctypes import windll, Structure, c_long, byref


listener_instance, pynput_listener = listener.start_listener()


WINDOW_TITLE = "Atalho"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600


# Window Resize classes and Functions
####################################
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return {"x": pt.x, "y": pt.y}


# Window Set size be %
def setsizer(window, perW, perH):
    user32 = windll.user32
    user32.SetProcessDPIAware()
    [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

    window.move(10, 10)

    w = w * (perW / 100)  # resize to 80% of user screen W
    y = h * (perH / 100)  # resize to 80% of user screen H
    window.resize(round(w), round(y))


####################################


class Api:
    def __init__(self):
        self.is_maximized = False
        self.is_window_open = True
        self.window = None
        self.is_resizing = False  # Add a state variable for resizing

    def close_window(self):
        self.is_window_open = False
        if webview.windows:
            self.window.destroy()
            listener.stop_keyboard_listener(listener_instance, pynput_listener)

    def minimize_window(self):
        window = get_window()
        if window:
            window.minimize()

    def maximize_or_restore_window(self):
        window = get_window()
        if window:
            if self.is_maximized:
                window.restore()
                self.window.evaluate_js(
                    'document.getElementById("maxRestore").children[0].src="/src/images/maxBtn_white.png"'
                )
            else:
                window.maximize()
                self.window.evaluate_js(
                    'document.getElementById("maxRestore").children[0].src="/src/images/restoreBtn_white.png"'
                )
                self.is_maximized = not self.is_maximized

    def create_and_position_window(self):
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        pos_x = (screen_width - WINDOW_WIDTH) // 2
        pos_y = (screen_height - WINDOW_HEIGHT) // 2

        self.window = webview.create_window(
            title=WINDOW_TITLE,
            url="index.html",
            frameless=True,
            resizable=True,
            js_api=self,
            min_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        # Wait a short moment for the window to be created
        time.sleep(1)

        # Find the window and move it
        window = get_window()
        if window:
            window.moveTo(pos_x, pos_y)

    # Handle Window Resize
    def start_resizing(self):
        self.is_resizing = True
        threading.Thread(
            target=self.doresize
        ).start()  # Start the resizing on a new thread

    def stop_resizing(self):
        self.is_resizing = False

    def doresize(self):
        # The doresize function now checks the is_resizing state variable
        # And runs in a loop until is_resizing is set to False
        state_left = windll.user32.GetKeyState(
            0x01
        )  # Left button down = 0 or 1. Button up = -127 or -128
        winWbefore = self.window.width
        winHbefore = self.window.height

        mouseactive = queryMousePosition()
        beforex = mouseactive["x"]
        beforey = mouseactive["y"]

        while self.is_resizing:
            mouseactive = queryMousePosition()
            afterx = mouseactive["x"]
            aftery = mouseactive["y"]
            try:
                totalx = int(beforex) - int(afterx)
                totaly = int(beforey) - int(aftery)

            except:
                print("fail")
            if totalx > 0:
                changerx = winWbefore + (totalx * -1)
            else:
                changerx = winWbefore + (totalx * -1)

            if totaly > 0:
                changerY = winHbefore + (totaly * -1)
            else:
                changerY = winHbefore + (totaly * -1)

            self.window.resize(changerx, changerY)

            time.sleep(0.01)


def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    # print(f"Found window: {windows}")
    return windows[0] if windows else None


def start_app():
    api = Api()
    api.create_and_position_window()

    # Create a new thread that waits for the window to be created and then calls inject_data
    def inject_data_after_delay():
        time.sleep(0.5)  # wait for the window to be created
        get_data_from_database()
        inject_data(api.window)

    threading.Thread(target=inject_data_after_delay).start()

    webview.start()


listener_thread = threading.Thread(target=KeyListener, daemon=True)
listener_thread.start()

try:
    start_app()
except Exception as e:
    print(f"An error occurred: {e}")

listener_thread.join()
