api = None  # Declare api as a global variable

import traceback

import glob
import webview
import threading
import time
import pygetwindow as gw
from screeninfo import get_monitors


from listener import KeyListener

# Import database
from src.database.data_connect import (
    get_database_path,
    get_db_files_in_directory,
    load_db_into_memory,
    save_db_from_memory,
)

from ctypes import windll, Structure, c_long, byref

# ------------------------------------ Save/Restore States
import json
import os
import logging
import sqlite3

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy import inspect
from threading import Lock

# --------------------------------------macros
from pynput import keyboard, mouse
from macroPlayer import Executor


# --------------------------------Imagem bandeja do sistema
import pystray
from PIL import Image

state_lock = Lock()


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Create an instance of KeyListener
# listener_instance = KeyListener()
# Start the listener in a new thread


WINDOW_TITLE = "Atalho"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700


# Get the absolute path of the directory the script is in.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script directory.
os.chdir(script_dir)


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
    engine = create_engine(f"sqlite:///{database_path}")
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
            # print(f"Fetched {len(rows)} row(s) from {tableName}:")
            for row in rows:
                # print(row)

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
        self.is_recording = False
        self.events = []
        self.listener_instance = KeyListener(self)
        self.listener = None
        self.mouse_listener = None
        self.last_event_time = None

        self.executor = Executor()
        self.execution_thread = None
        self.should_execute = False

    def minimize_window(self):
        self.window.minimize()

    def get_events(self):
        # Initialize an empty list to hold the events with intervals
        events_with_intervals = []

        # Iterate through the events
        for i in range(len(self.events) - 1):  # Subtract 1 here to avoid an IndexError
            event = self.events[i]
            next_event = self.events[i + 1]

            # Calculate the interval as the difference in elapsed time between the next event and this one
            interval = next_event[2] - event[2]

            # Add the event to the list, along with the interval until the next event
            events_with_intervals.append((event[0], event[1], interval))

        # Add the last event manually to avoid an IndexError
        if self.events:  # Check if the list is not empty
            last_event = self.events[-1]
            events_with_intervals.append((last_event[0], last_event[1], 0))

        # Return the modified list of events
        return events_with_intervals

    def clear_events(self):
        self.events = []

    def is_recording(self):
        return self.is_recording

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.stop_recording()

        if self.is_recording:
            current_time = time.time()
            elapsed_time = (
                current_time - self.start_time if self.start_time is not None else 0
            )
            self.events.append(("key", str(key), elapsed_time))

    def on_click(self, x, y, button, pressed):
        if self.is_recording and pressed:
            current_time = time.time()
            elapsed_time = (
                current_time - self.start_time if self.start_time is not None else 0
            )
            self.events.append(("click", (x, y), elapsed_time))

    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()

        listener_instance.startRecordingMacro()

        # Stop the global listener
        listener_instance.stop_listener()

        self.events = []

        # Check if the listeners already exist and stop them if they do
        if self.listener is not None:
            self.listener.stop()
        if self.mouse_listener is not None:
            self.mouse_listener.stop()

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

    def stop_recording(self):
        self.is_recording = False
        listener_instance.stopRecordingMacro()
        # Start the global listener
        listener_instance.start_listener()

        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

    def save_macro(self, filename):
        # Get the path to the current file (__file__)
        current_file_path = os.path.abspath(__file__)

        # Get the parent directory of the current file
        parent_directory = os.path.dirname(current_file_path)

        # Get the path to the macros directory
        macros_directory = os.path.join(parent_directory, "src", "macros")

        # Create the full file path
        full_file_path = os.path.join(macros_directory, filename)

        # Save your recording to the file
        # ...
        try:
            with open(full_file_path, "w") as f:
                json.dump(self.events, f)
            return full_file_path
        except Exception as e:
            print(f"An error occurred while saving the macro: {e}")
            return None

    # ---------------------------------------------------------------- EXECUÇAO MACROs--------------------------------

    def get_macro_filename(self):
        return self.executor.get_macro_filename()

    def start_macro(self, filename):
        self.executor.start_macro(filename)

    # ----------------------------------------------------------------   --------------------------------
    def get_database_names(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        groups_dir = os.path.join(base_dir, "groups")
        database_files = glob.glob(os.path.join(groups_dir, "*.db"))
        database_names = [
            os.path.splitext(os.path.basename(db_file))[0] for db_file in database_files
        ]

        return database_names

    def get_all_db_files(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        groups_dir = os.path.join(base_dir, "src", "database", "groups")
        subdirectories = [f.path for f in os.scandir(groups_dir) if f.is_dir()]

        all_db_files = {}
        for subdirectory in subdirectories:
            db_files = [
                os.path.splitext(os.path.basename(db_file))[0]
                for db_file in get_db_files_in_directory(subdirectory)
            ]
            directory_name = os.path.basename(subdirectory)
            all_db_files[directory_name] = db_files

            # Encode the directory name and .db files as JSON
            encoded_directory = json.dumps(directory_name)
            encoded_db_files = json.dumps(db_files)

            # Call createCollapsible in JavaScript for this directory and its .db files
            self.window.evaluate_js(
                f"createCollapsible({encoded_directory}, {encoded_db_files});"
            )

        return all_db_files

    def get_data(self, groupName, databaseName, tableName):
        print("get_data called with", groupName, databaseName, tableName)
        try:
            rows = handle_database_operations(groupName, databaseName, tableName)
            return rows
        except Exception as e:
            print(f"Error in get_data: {e}")
            print(traceback.format_exc())
            return None

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

    def create_and_position_window(self):
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        pos_x = (screen_width - WINDOW_WIDTH) // 2
        pos_y = (screen_height - WINDOW_HEIGHT) // 2

        self.window = webview.create_window(
            title=WINDOW_TITLE,
            url="index.html",
            frameless=False,
            resizable=True,
            js_api=self,
            min_size=(screen_width // 2, WINDOW_HEIGHT),
        )

        time.sleep(1)

        window = get_window()

        if window:
            window.moveTo(pos_x, pos_y)

        threading.Thread(target=self.call_load_handler_after_delay).start()

    def call_load_handler_after_delay(self):
        time.sleep(0.5)
        load_handler(self.window)


api = Api()
listener_instance = KeyListener(api)


def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    return windows[0] if windows else None


def load_handler(window):
    pass


def start_app():
    global api  # Add this line
    api = Api()
    api.create_and_position_window()
    webview.start(http_server=True)


# Start the listener in a new thread
listener_thread = threading.Thread(target=listener_instance.start_listener, daemon=True)
listener_thread.start()

try:
    start_app()
except Exception as e:
    print(f"An error occurred: {e}")

listener_thread.join()
