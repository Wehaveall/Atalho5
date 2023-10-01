
import queue
import keyboard  # Replacing pynput
import webview
import pygetwindow as gw
from functools import partial

from pygetwindow import getActiveWindow  # Add this import at the top of your code file

import pyautogui
from src.database.data_connect import lookup_word_in_all_databases

import pyperclip  # We add this import for clipboard manipulation
from src.utils import number_utils
import time
import logging
import ctypes





from collections import deque

import threading

import time

import json

#######################################
######################### POP UP FOR MULTIPLE EXPANSIONS
from src.classes.popup import (CustomTkinterPopupSelector,)  # Adjust the import based on your directory structure

import tkinter as tk
from tkinter import Button
import customtkinter as ctk





import customtkinter as ctk  # Import customtkinter instead of tkinter







api = None  # Declare api as a global variable

# pywebview
import webview

# Dialog box
import tkinter
from tkinter import messagebox
from tkinter import font

# custom message box
from tkinter import Toplevel, Label, Button, PhotoImage


import traceback

import glob
import webview
import threading
import time
import pygetwindow as gw
from screeninfo import get_monitors


from listener import (
    KeyListener,
)  # Make sure this is your new KeyListener with the keyboard library

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


from sqlalchemy.orm import Session


from sqlalchemy import create_engine, MetaData, Table, select, update
from sqlalchemy import inspect
from threading import Lock


from src.classes.popup import (
    CustomTkinterPopupSelector,
)  # Adjust the import based on your directory structure


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


def msg(title, message):
    # No need to create a root Tk() instance with tkinter.messagebox
    messagebox.showinfo(title, message)


def msgOC(title, message):
    # Create a root window and immediately withdraw it (hide it)
    root = tkinter.Tk()
    root.withdraw()

    result = messagebox.askokcancel(title, message)

    if result:
        print("User clicked OK")
    else:
        print("User clicked Cancel")

    # Destroy the root window
    root.destroy()

    # Return the result
    return result


##--------------------------------------------------------------------------


class Api:
    def __init__(self):
        

        self.is_maximized = False
        self.is_window_open = True
        self.is_recording = False
        self.events = []

        self.last_event_time = None

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
    return text[:max_length - 3] + "..." if len(text) > max_length else text


def create_popup(tk_queue, key_listener_instance):
    print("Entered create_popup")  # Debugging
    while True:
        queue_data = tk_queue.get()
        msg, data = queue_data[:2]  # Only take the first two values

        current_window = getActiveWindow()
        current_win_title = current_window.title if current_window else "Unknown Window"
        
        if msg == "create_popup":
            print("About to stop listener and create popup")  # Debugging
            key_listener_instance.stop_listener()

            windows = gw.getWindowsWithTitle(current_win_title)
            if windows:
                main_win = windows[0]
                pyautogui.click(main_win.left + 10, main_win.top + 10)
            else:
                print(f"No window with title '{current_win_title}' found.")

            popup = ctk.CTk()  # Use ctk instead of tk
            popup.title("Select Expansion")

            for i, option in enumerate(key_listener_instance.expansions_list):
                raw_button_text = option['expansion'] if 'expansion' in option else "Undefined"
                button_text = truncate_text(raw_button_text, 60)
                button = ctk.CTkButton(
                    popup,
                    text=button_text,
                    command=partial(key_listener_instance.make_selection, i, popup),
                    font=("Work Sans", 12),
                    anchor="w"
                )
                button.pack(fill=ctk.X, padx=10, pady=5)

            # Update idle tasks to get updated dimensions
            popup.update_idletasks()

            # Get the content width and height
            content_width = 400
            content_height = popup.winfo_height()

              # Get the caret's screen coordinates
            caret_x, caret_y = get_caret_position()

                # Set the popup window's position to be 20 pixels below the y-coordinate of the caret
            popup.geometry(f"{content_width}x{content_height}+{caret_x}+{caret_y + 120}")

          
         
            def on_closing():
                try:
                    print("Trying to restart the listener...")  # Debugging
                    key_listener_instance.start_listener()  # Start the listener
                except Exception as e:
                    print(f"Failed to restart listener. Exception: {e}")
                finally:
                    popup.destroy()

            popup.protocol("WM_DELETE_WINDOW", on_closing)
            print("Setting WM_DELETE_WINDOW protocol")  # Debugging

            popup.attributes("-topmost", True)
            popup.focus_force()

            print("Entering Tkinter mainloop")  # Debugging
            popup.mainloop()





def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    return windows[0] if windows else None


def load_handler(window):
    pass







def start_app(tk_queue):
    global api  # Existing line
    api = Api()  # Existing line
    api.create_and_position_window()  # Existing line

    key_listener_instance = KeyListener(api, tk_queue)  # Moved inside start_app
    key_listener_thread = threading.Thread(target=key_listener_instance.start_listener)
    key_listener_thread.start()

    # Pass the key_listener_instance to create_popup
    threading.Thread(target=create_popup, args=(tk_queue, key_listener_instance)).start()

    print("Starting Listener from Main.py")  # Existing line
    
    
   
    
    try:
        webview.start(http_server=True)
   
    finally:
        print('Cleanup function called.')
        key_listener_instance.stop_listener()
        key_listener_thread.join() 
           
   
   
   
   

 









def main():
    tk_queue = queue.Queue()  # Make sure to import the 'queue' module

    # Initialize Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Create a thread to run Tkinter event loop
    #threading.Thread(target=create_popup, args=(tk_queue, key_listener_instance)).start()


    # Call start_app
    start_app(tk_queue)

    root.mainloop()
    


# Start the application
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
