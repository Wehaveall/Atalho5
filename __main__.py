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
    get_database_path,
    get_db_files_in_directory,
    inject_data,
    load_db_into_memory,
    save_db_from_memory,
)

from ctypes import windll, Structure, c_long, byref

# Save/Restore States
import json
import os
import logging
import sqlite3

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy import inspect
from threading import Lock

state_lock = Lock()

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


# Add a function to handle database operations
from sqlalchemy import inspect


def handle_database_operations(groupName, databaseName, tableName):
    database_path = get_database_path(groupName, databaseName)
    engine = create_engine(
        f"sqlite:///./src/database/groups/{groupName}/{databaseName}"
    )
    metadata = MetaData()

    try:
        # Ensure tableName is a string, not a list
        if isinstance(tableName, list) and len(tableName) == 1:
            tableName = tableName[0]

        with Session(engine) as session:
            table = Table(tableName, metadata, autoload_with=engine)
            result = session.execute(select(table)).fetchall()
            session.commit()

            # Convert the results into a list of dictionaries
            # Modified this line to use row2dict
            rows = [row2dict(row) for row in result]

            # Print the rows for debugging
            print(f"Fetched {len(rows)} row(s) from {tableName}:")
            for row in rows:
                print(row)

            return rows

    except Exception as e:
        print(f"An error occurred: {e}")

        # If the table doesn't exist, print the available tables for debugging
        inspector = inspect(engine)
        print(f"Available tables in {databaseName}: {inspector.get_table_names()}")

        return None


def row2dict(row):
    """Convert a SQLAlchemy RowProxy into a dictionary."""
    return dict(row._mapping)


##--------------------------------------------------------------------------


class Api:
    def __init__(self):
        self.is_maximized = False
        self.is_window_open = True
        self.window = None
        self.is_resizing = False  # Add a state variable for resizing

    def get_database_names(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        groups_dir = os.path.join(base_dir, "groups")
        database_files = glob.glob(os.path.join(groups_dir, "*.db"))
        database_names = [os.path.basename(db_file) for db_file in database_files]

        return database_names

    def get_all_db_files(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        groups_dir = os.path.join(base_dir, "groups")
        subdirectories = [f.path for f in os.scandir(groups_dir) if f.is_dir()]

        all_db_files = {}
        for subdirectory in subdirectories:
            db_files = get_db_files_in_directory(subdirectory)
            directory_name = os.path.basename(subdirectory)
            all_db_files[directory_name] = db_files

        return all_db_files

    def get_data(self, groupName, databaseName, tableName):
        rows = handle_database_operations(groupName, databaseName, tableName)
        return rows

    def get_tables(self, groupName, databaseName):
        conn = sqlite3.connect(get_database_path(groupName, databaseName))
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        conn.close()
        return tables

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

    def load_all_states(self):
        if not os.path.exists("state.json"):
            return {}
        with state_lock:
            with open("state.json", "r") as file:
                data = json.load(file)
                return data

    def save_all_states(self, states):
        with state_lock:
            with open("state.json", "w") as file:
                json.dump(states, file)

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
            monitor = get_monitors()[0]
            screen_width = monitor.width
            screen_height = monitor.height
            window_size = window.size

            if window_size.width < screen_width or window_size.height < screen_height:
                window.maximize()
                self.window.evaluate_js(
                    'document.getElementById("maxRestore").children[0].src="/src/images/restoreBtn_white.png"'
                )
            else:
                window.restore()
                self.window.evaluate_js(
                    'document.getElementById("maxRestore").children[0].src="/src/images/maxBtn_white.png"'
                )

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
            min_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        time.sleep(1)

        window = get_window()
        if window:
            window.moveTo(pos_x, pos_y)

        threading.Thread(target=self.call_load_handler_after_delay).start()

    def call_load_handler_after_delay(self):
        time.sleep(0.5)
        load_handler(self.window)

    def start_resizing(self):
        self.is_resizing = True
        threading.Thread(target=self.doresize).start()

    def stop_resizing(self):
        self.is_resizing = False

    def doresize(self):
        state_left = windll.user32.GetKeyState(0x01)
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
