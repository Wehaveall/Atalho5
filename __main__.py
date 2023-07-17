api = None  # Declare api as a global variable


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
    get_database_path,
    insert_into_db,
    get_data,
    inject_data,
)

from ctypes import windll, Structure, c_long, byref

# Save/Restore States
import json
import os
import logging
import sqlite3


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

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

    def get_data(self, databaseName):
        # Connect to SQLite database
        conn = sqlite3.connect(get_database_path(databaseName))

        # Create a cursor object
        c = conn.cursor()

        # Execute an SQL command
        c.execute("SELECT * FROM myTable")

        # Fetch all rows from the last executed SQL command
        rows = c.fetchall()

        # Convert each tuple to a list
        rows_as_list = [list(row) for row in rows]

        # Don't forget to close the connection
        conn.close()

        return rows_as_list

    # Loading Translations

    def load_translations(self):
        try:
            logging.debug("load_translations called")
            with open("languages.json", encoding="utf-8") as f:
                translations = json.load(f)
                language = self.load_language_setting()
                logging.debug(f"load_translations loaded language: {language}")
                return translations.get(language, {})
        except Exception as e:
            logging.error(f"Error in load_translations: {e}")

    def load_language_setting(self):
        try:
            logging.debug("load_language_setting called")
            with open("settings.json", "r") as f:
                settings = json.load(f)
            language = settings.get("language", "en")  # Default to 'en' if not found
            logging.debug(f"load_language_setting loaded language: {language}")
            return language
        except Exception as e:
            logging.error(f"Error in load_language_setting: {e}")

    def change_language(self, language_code):
        try:
            logging.debug(f"change_language called with language code: {language_code}")
            settings = {"language": language_code}
            with open("settings.json", "w") as f:
                json.dump(settings, f)
            logging.debug(f"change_language changed language to: {language_code}")
            return {"language": language_code}
        except Exception as e:
            logging.error(f"Error in change_language: {e}")

    # -----------------------Por enquanto, caregando o state do collapsible	Left Panel - state.json
    def load_state(self, directory):
        # In the loadState method, if state.json does not exist,
        # the method will return "none". This is done using:

        if not os.path.exists("state.json"):
            return "none"

        with open("state.json", "r") as file:
            data = json.load(file)
            return data.get(directory, "none")

    # -----------------------Por enquanto, salvando o state do collapsible	Left Panel - state.json

    def save_state(self, directory, state):
        # In the saveState method, if state.json does not exist, a new dictionary
        #  is created to store the data. This is done using:

        if not os.path.exists("state.json"):
            data = {}
        else:
            with open("state.json", "r") as file:
                data = json.load(file)

        data[directory] = state
        with open("state.json", "w") as file:
            json.dump(data, file)

    # ------------------------------------------Fechar Janela
    def close_window(self):
        self.is_window_open = False
        if webview.windows:
            self.window.destroy()
            listener.stop_keyboard_listener(listener_instance, pynput_listener)

    # ----------------------------------------Minimizar Janela
    def minimize_window(self):
        window = get_window()
        if window:
            window.minimize()

    # -----------------------------------------Maximizar, Restaura Janela
    def maximize_or_restore_window(self):
        window = get_window()
        if window:
            monitor = get_monitors()[0]
            screen_width = monitor.width
            screen_height = monitor.height
            window_size = window.size

            if window_size.width < screen_width or window_size.height < screen_height:
                # The window is not maximized, so maximize it
                window.maximize()
                self.window.evaluate_js(
                    'document.getElementById("maxRestore").children[0].src="/src/images/restoreBtn_white.png"'
                )
            else:
                # The window is maximized, so restore it
                window.restore()
                self.window.evaluate_js(
                    'document.getElementById("maxRestore").children[0].src="/src/images/maxBtn_white.png"'
                )

    # ----------------------------Criar e posicionar janela

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
            js_api=api,
            # The Python webview package provides an option to bind Python methods to JavaScript functions through
            # the js_api parameter of the webview.create_window() function.
            # In the main.py file you provided, an instance of the Api class is passed as the js_api parameter.
            #  This means that all methods of the Api class are available to be called from JavaScript.
            # You can add a new method to the Api class to load the translations from a JSON file and return them.
            #  This method can then be called from JavaScript to get the translations.
            min_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        # Wait a short moment for the window to be created
        time.sleep(1)

        # Find the window and move it
        window = get_window()
        if window:
            window.moveTo(pos_x, pos_y)

        threading.Thread(target=self.call_load_handler_after_delay).start()

    def call_load_handler_after_delay(self):
        time.sleep(0.5)  # wait for the window to be ready
        load_handler(self.window)

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
    return windows[0] if windows else None


def load_handler(window):
    global api
    inject_data(window)


def start_app():
    global api
    api = Api()
    api.create_and_position_window()
    webview.start(http_server=True)


listener_thread = threading.Thread(target=KeyListener, daemon=True)
listener_thread.start()

try:
    start_app()
except Exception as e:
    print(f"An error occurred: {e}")

listener_thread.join()
