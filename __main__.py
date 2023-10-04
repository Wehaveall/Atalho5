# Standard Library Imports
from collections import deque
from ctypes import windll, Structure, c_long, byref
from functools import partial
import ctypes
from queue import SimpleQueue, Empty
import glob
import json
import logging
import os
from threading import enumerate as list_threads, Lock
import queue
import sys
import threading
import time
import traceback

# Third-Party Imports
from pywinauto import Application
import customtkinter as ctk
import keyboard
import pyautogui
import pygetwindow as gw
import pyperclip
from screeninfo import get_monitors
from sqlalchemy import create_engine, MetaData, Table, select, update, inspect
from sqlalchemy.orm import Session
import tkinter as tk
from tkinter import Toplevel, Label, Button, PhotoImage, messagebox, font
import webview

# Custom Module Imports
from listener import KeyListener
from shared_variables import should_close_popup
from src.classes.popup import CustomTkinterPopupSelector
from src.database.data_connect import (
    get_database_path,
    get_db_files_in_directory,
    load_db_into_memory,
    save_db_from_memory,
    lookup_word_in_all_databases,
)
from src.utils import number_utils

# Global Variable Initialization
api = None



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


# Use an Event object to signal all threads to stop
# Declaring variable as global
stop_threads = threading.Event()


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


# Dicionário global para armazenar engines
# Removendo a criação duplicada do dicionário engines e função get_engine
engines = {}


def get_engine(database_path):
    """Retorna uma engine existente ou cria uma nova baseada no caminho do banco de dados."""
    if database_path not in engines:
        engines[database_path] = create_engine(f"sqlite:///{database_path}")
    return engines[database_path]


# --------------------------------------------------------------------------------------------------------------------


def handle_database_operations(groupName, databaseName, tableName=None):
    database_path = get_database_path(groupName, databaseName)
    engine = get_engine(database_path)  # Usando get_engine em vez de create_engine
    metadata = MetaData()

    # Se tableName não for fornecido, determinar o nome da tabela que não é "sqlite_sequence"
    if not tableName:
        with engine.connect() as conn:
            table_names = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';"
            ).fetchall()
            if table_names:
                tableName = table_names[0][0]
            else:
                print("No valid table found.")
                return []

    try:
        with Session(engine) as session:
            table = Table(tableName, metadata, autoload_with=engine)
            result = session.execute(select(table)).fetchall()
            # Converta os resultados em uma lista de dicionários
            return [row2dict(row) for row in result]

    except Exception as e:
        print(f"Error handling operations for table {tableName}: {e}")
        return []


# ---------------------------------------------------------------------------------------------------------
# #----------------------------------------------------------------------------
def row2dict(row):
    """Convert a SQLAlchemy RowProxy into a dictionary."""
    return dict(row._mapping)


# Pegar o caminho relatiov ao programa do arquivo
def get_relative_path(filename):
    # Get the path of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Combine the script directory with the filename
    return os.path.join(script_dir, filename)




##--------------------------------------------------------------------------


class Api:
    def __init__(self):
        self.is_maximized = False
        self.is_window_open = True
        self.is_recording = False
        self.events = []

        self.last_event_time = None

    def on_closed(self):
        print("on_closed triggered")
        stop_threads.set()

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

    # ---------------------------------------------------------------- DATABASE  -------------------------------------
    # --------------------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------------------

    def save_changes(
        self,
        groupName,
        databaseName,
        tableName,
        shortcut,
        newContent,
        formatValue,
        label,
        caseChoice=None,  # New parameter
    ):
        # Convert formatValue to 0 or 1 for SQLite storage
        format_value_for_db = 1 if formatValue else 0
        print(
            f"Converted format value for DB: {format_value_for_db}"
        )  # Just for debugging

        # Get the engine for the specified database path
        database_path = get_database_path(groupName, databaseName)
        engine = get_engine(database_path)  # Using get_engine instead of create_engine
        metadata = MetaData()

        with Session(engine) as session:
            # Get the table names from the database using inspect
            table_names = inspect(engine).get_table_names()

            # Filter out 'sqlite_sequence' and 'config' and get the desired table name
            desired_table_name = next(
                (
                    name
                    for name in table_names
                    if name not in ["sqlite_sequence", "config"]
                ),
                tableName,
            )

            # Target the desired table
            table = Table(desired_table_name, metadata, autoload_with=engine)

            # Prepare the update statement
            update_values = {
                "format": format_value_for_db,
                "case": caseChoice,
            }  # Add case field update

            # If newContent is provided, update the expansion column
            if newContent:
                update_values["expansion"] = newContent

            # If labelText is provided, update the label column
            if label:
                update_values["label"] = label

            stmt = (
                update(table)
                .where(table.c.shortcut == shortcut)
                .values(**update_values)
            )

            # Execute the update statement
            print("Saving changes to the database...")
            session.execute(stmt)
            session.commit()
            print("Changes saved successfully!")

            # Notify JavaScript to invalidate the cache after updating the database
            self.window.evaluate_js(
                'invalidateCacheEntry("{groupName}", "{databaseName}", "{tableName}")'.format(
                    groupName=groupName, databaseName=databaseName, tableName=tableName
                )
            )

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

    # ----------------------------------------------------------------EXCLUIR - SQLITE_SEQUENCY AND CONFIG TABLE
    def get_target_table_name(self, engine):
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        for name in table_names:
            if name not in ["sqlite_sequence", "config"]:
                return name
        return None  # If no table is found other than 'sqlite_sequence' and 'config'

    # -------------------------------------------------------------------

    # Configurar o logging
    logging.basicConfig(filename="app.log", level=logging.INFO)

    def get_data(self, groupName, databaseName, tableName):
        try:
            # Obter o caminho do banco de dados
            database_path = get_database_path(groupName, databaseName)

            # Usar get_engine para obter uma instância de engine
            engine = get_engine(database_path)

            # Se tableName é None, obtenha o nome da tabela que não é 'sqlite_sequence'
            if tableName is None:
                tableName = api.get_target_table_name(engine)
                if not tableName:
                    logging.error("No valid table found other than sqlite_sequence.")
                    return None

            # Tratar operações no banco de dados
            rows = handle_database_operations(groupName, databaseName, tableName)
            return rows

        except Exception as e:
            logging.error(f"Error in get_data: {e}")
            logging.error(traceback.format_exc())
            return None

    # -------------------------------------------------------------------------------------------

    def get_tables(self, groupName, databaseName):
        database_path = get_database_path(groupName, databaseName)
        engine = get_engine(database_path)  # Usando get_engine em vez de create_engine
        metadata = MetaData()

        with engine.connect() as conn:
            metadata.reflect(
                bind=engine
            )  # Reflect the state of the database into the metadata
            table_names = metadata.tables.keys()

            # Filter out the tables "sqlite_sequence" and "config"
            return [
                name
                for name in table_names
                if name not in ["sqlite_sequence", "config"]
            ]

    # ----------------------------------------------------------------SETTINGS----------------------------------------------------------------

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

    def save_checkBox_states(self, checkBoxStates):
        with open("checkBox_states.json", "w", encoding="utf-8") as f:
            json.dump(checkBoxStates, f, ensure_ascii=False)
        # print("Saved checkbox states.")

    def load_checkBox_states(self):
        filePath = "checkBox_states.json"
        if os.path.exists(filePath):
            with open(filePath, "r", encoding="utf-8") as f:
                checkBoxStates = json.load(f)
            # print(f"Loaded checkbox states from {filePath}")
        else:
            print(f"{filePath} not found. Initializing empty checkbox states.")
            checkBoxStates = {}

        return checkBoxStates

    # ----------------------------------------------------------------CREATE WINDOW

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
        return self.window

    def call_load_handler_after_delay(self):
        time.sleep(0.5)
        load_handler(self.window)


# Define POINT structure
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


# Load necessary DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def get_caret_position():
    """Get the screen coordinates of the caret in the currently active window."""

    # Get current thread ID from kernel32.dll
    current_thread_id = kernel32.GetCurrentThreadId()

    # Get the window handle for the current foreground window
    foreground_window = user32.GetForegroundWindow()

    # Get the thread ID of the process that created the window
    window_thread_id = user32.GetWindowThreadProcessId(foreground_window, None)

    # Attach the current thread to the window's thread to share input states
    user32.AttachThreadInput(current_thread_id, window_thread_id, True)

    # Initialize POINT for caret position
    caret_pos = POINT()

    # Get the caret's position
    user32.GetCaretPos(ctypes.byref(caret_pos))

    # Get the window handle that has the keyboard focus
    focused_window = user32.GetFocus()

    # Convert the caret's position to screen coordinates
    user32.ClientToScreen(focused_window, ctypes.byref(caret_pos))

    # Detach the current thread from the window's thread
    user32.AttachThreadInput(current_thread_id, window_thread_id, False)

    return (caret_pos.x, caret_pos.y)


def truncate_text(text, max_length):
    return text[: max_length - 3] + "..." if len(text) > max_length else text


def create_popup(tk_queue, key_listener_instance):
    print("Entered create_popup")
    root = None
    should_create_popup = False  # Add this flag

    def destroy_popup():
        print("destroy_popup called")  # Debug print
        nonlocal root, should_create_popup  # Add should_create_popup here
        print(f"Root is None: {root is None}")  # Debug print

        if root is not None:
            print("Received message: destroy_popup")
            root.destroy()
            # Restart the keyboard listener here
            should_create_popup = False  # Reset the flag when destroying the popup

            try:
                key_listener_instance.start_listener()  # Assuming `start_listener` is the method to restart the listener
                print("Listener restarted successfully")
            except Exception as e:
                print(f"Failed to restart the listener: {e}")

    def create_popup_internal():
        nonlocal root, should_create_popup  # Add should_create_popup here
        print("About to stop listener and create popup")
        key_listener_instance.stop_listener()

        root = tk.Tk()
        root.title("Select Expansion")
        # Register the destroy_popup function for the close button
        root.protocol("WM_DELETE_WINDOW", destroy_popup)  # Add this line

        caret_x, caret_y = get_caret_position()

        print(f"Caret position: x={caret_x}, y={caret_y}")

        # Set the window size and position it below the caret
        window_width = 500
        window_height = 300
        root.geometry(f"{window_width}x{window_height}+{caret_x}+{caret_y}")

        root.attributes("-topmost", True)  # This line makes the window stay on top
        # root.grab_set()  # This line captures all events
        # Make sure the window is created
        root.update_idletasks()
        root.update()

        for i, option in enumerate(key_listener_instance.expansions_list):
            raw_button_text = (
                option["expansion"] if "expansion" in option else "Undefined"
            )
            button_text = truncate_text(raw_button_text, 60)
            button = Button(
                root,
                text=button_text,
                command=partial(key_listener_instance.make_selection, i, root),
                font=("Work Sans", 11),
                anchor="w",
            )
            button.pack(fill=tk.X, padx=10, pady=5)
        should_create_popup = True  # Set the flag to True when the popup is created

        ## Simulate the mouse click to focus the popup window
        windows = gw.getWindowsWithTitle("Select Expansion")
        if windows:
            popup_win = windows[0]
            pyautogui.click(popup_win.left + 10, popup_win.top + 10)

    while not stop_threads.is_set():
        try:
            queue_data = tk_queue.get(timeout=0.5)

            msg = queue_data[0]

            if msg == "destroy_popup":
                destroy_popup()
                continue
            if msg == "create_popup":
                create_popup_internal()

        except Empty:
            continue

        if should_create_popup:  # Check the flag before running the main loop
            root.mainloop()
            should_create_popup = (
                False  # Reset the flag after the main loop is terminated
            )

    print("Popup thread stopped")


def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    return windows[0] if windows else None


def load_handler(window):
    pass


def keyboard_listener(key_listener_instance):
    key_listener_instance.start_listener()  # Start the listener using your class method
    while not stop_threads.is_set():
        # print("Keyboard listener is running")  # Debugging line
        time.sleep(0.1)
    key_listener_instance.stop_listener()  # Stop the listener using your class method
    print("Keyboard listener stopped")


def start_app(tk_queue):
    global api  # Existing line
    api = Api()  # Existing line
    # api.create_and_position_window()  # Existing line

    # Move this line up to initialize before starting the threads
    key_listener_instance = KeyListener(api, tk_queue)  # Moved inside start_app

    # --------Start Pop-Up Thread
    global stop_threads
    popup_thread = threading.Thread(
        target=create_popup,
        args=(tk_queue, key_listener_instance),
        name="Pop-Up Thread",
    )

    popup_thread.daemon = True  # Set daemon status
    popup_thread.start()

    # --------Start Key Listener Thread
    key_listener_thread = threading.Thread(
        target=keyboard_listener,
        args=(key_listener_instance,),
        name="KeyBoard Listener Thread",
    )

    key_listener_thread.daemon = True  # Set daemon status
    key_listener_thread.start()
    # Pass the key_listener_instance to create_popup

    # threading.Thread(target=create_popup, args=(tk_queue, key_listener_instance)).start()
    print("Starting Listener from Main.py")  # Existing line
    main_window = api.create_and_position_window()  # Existing line
    main_window.events.closed += api.on_closed

    webview.start(http_server=True)

    print("Cleanup function called.")

    print("About to join threads")
    popup_thread.join()
    key_listener_thread.join()

    while True:
        active_threads = [t for t in threading.enumerate() if t.is_alive()]

        # Check if the key_listener and popup threads are still active
        key_listener_active = any(
            t.name == "KeyBoard Listener Thread" for t in active_threads
        )
        popup_active = any(t.name == "Pop-Up Thread" for t in active_threads)

        # If both are no longer active, break the loop
        if not key_listener_active and not popup_active:
            print("Key listener and Popup threads have terminated.")
            break

        for thread in active_threads:
            print(f"Thread {thread.name} is still active.")

        stop_threads.set()

        time.sleep(1)

    print("Exiting main thread.")
    sys.exit()


# Start the application
if __name__ == "__main__":
    try:
        tk_queue = queue.Queue()
        start_app(tk_queue)

    except Exception as e:
        print(f"An error occurred: {e}")
