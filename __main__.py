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

listener_instance, pynput_listener = listener.start_listener()

WINDOW_TITLE = "Atalho"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class Api:
    def __init__(self):
        self.is_maximized = False
        self.is_window_open = True
        self._window = None

    def close_window(self):
        self.is_window_open = False
        if webview.windows:
            webview.windows[0].destroy()
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
            else:
                window.maximize()
            self.is_maximized = not self.is_maximized


def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    return windows[0] if windows else None


def create_and_position_window(api):
    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height
    pos_x = (screen_width - WINDOW_WIDTH) // 2
    pos_y = (screen_height - WINDOW_HEIGHT) // 2

    window = webview.create_window(
        title=WINDOW_TITLE,
        url="index.html",
        frameless=True,
        resizable=True,
        js_api=api,
        min_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
    )
    webview_window = webview.windows[0]  # Save the WebView window
    # Wait a short moment for the window to be created
    time.sleep(1)

    # Find the window and move it
    window = get_window()
    if window:
        window.moveTo(pos_x, pos_y)

    return webview_window


def start_app():
    api = Api()
    webview_window = create_and_position_window(api)  # store the returned window object

    # Create a new thread that waits for the window to be created and then calls inject_data
    def inject_data_after_delay():
        time.sleep(0.5)  # wait for the window to be created
        get_data_from_database()
        inject_data(webview_window)

    threading.Thread(target=inject_data_after_delay).start()

    webview.start()


# create_db()
# insert_into_db('shortcut_example', 'large formated text', 'label_example')

listener_thread = threading.Thread(target=KeyListener, daemon=True)
listener_thread.start()

try:
    start_app()
except Exception as e:
    print(f"An error occurred: {e}")

listener_thread.join()
