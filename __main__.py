api = None  # Declare api as a global variable

import pywebview


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

# Save/Restore States
import json
import os


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

    # Loading Translations

    def load_translations(self, window):
        with open("languages.json") as f:
            translations = json.load(f)
        return translations

    def load_language_setting(self, window):
        with open("settings.json", "r") as f:
            settings = json.load(f)
        return settings["language"]

    def change_language(self, language_code):
        self.window.currentLanguage = language_code
        self.set_language(self.window)  # passing self.window as the argument
        self.update_language(self.window)  # using self.window here as well
        self.save_language_setting(language_code)  # Save the selected language

    def set_language(self, window):
        set_language_js = """
        function setLanguage(languageCode) {
        window.currentLanguage = languageCode;
        updateLanguage();
        }
        """
        self.window.evaluate_js(set_language_js)
        self.window.evaluate_js(f"setLanguage('{self.window.currentLanguage}')")

    def update_language(self, window):
        update_language_js = """
        function updateLanguage() {
        document.querySelectorAll('.tablinks').forEach(button => {
            const tabName = button.getAttribute('onclick').split("'")[1];
            button.textContent = translations[currentLanguage][tabName];
        });
        }
        """
        self.window.evaluate_js(update_language_js)
        self.window.evaluate_js("updateLanguage()")

    ...

    def save_language_setting(self, language_code):
        print("Saving language setting")  # Debugging print statement
        print(f"Language Code: {language_code}")  # Debugging print statement
        settings = {"language": language_code}
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error writing to settings.json: {e}")
        return {}

    # -----------------------Por enquanto, caregando o state do collapsible	Left Panel - state.json
    def loadState(self, directory):
        # In the loadState method, if state.json does not exist,
        # the method will return "none". This is done using:

        if not os.path.exists("state.json"):
            return "none"

        with open("state.json", "r") as file:
            data = json.load(file)
            return data.get(directory, "none")

    # -----------------------Por enquanto, salvando o state do collapsible	Left Panel - state.json

    def saveState(self, directory, state):
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
    api.load_translations(window)

    # Load preferred language from a JSON file
    with open("settings.json", "r") as f:
        settings = json.load(f)
    preferred_language = settings.get("language")  # default to 'en' if not found

    api.change_language(preferred_language)
    api.update_language(window)  # Use the passed `window` argument
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
