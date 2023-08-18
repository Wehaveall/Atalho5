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


from sqlalchemy import create_engine, MetaData, Table, select, update
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
        self.listener_instance = KeyListener(self)
        self.listener = None
        self.mouse_listener = None
        self.last_event_time = None

        # Execução da Macro
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
        # Se está gravando
        if self.is_recording:
            # Se apertou escape
            if key == keyboard.Key.esc:
                self.stop_recording()
                msg("Atalho", "Gravação Parada.")
                # show_message("Atalho", "Gravação Parada.")

            else:
                # If any other key is pressed, add it to the events list
                current_time = time.time()
                elapsed_time = current_time - self.start_time if self.start_time else 0
                self.events.append(("key", str(key), elapsed_time))

    def on_click(self, x, y, button, pressed):
        if self.is_recording and pressed:
            current_time = time.time()
            elapsed_time = (
                current_time - self.start_time if self.start_time is not None else 0
            )
            self.events.append(("click", (x, y), elapsed_time))

    # ----------------------------------------------------------------START RECORDING
    # ----------------------------------------------------------------

    def start_recording(self):
        confirmation = msgOC(
            "Atalho",
            "Ao clicar em OK, a janela do Atalho será minimizada e a gravação da macro será iniciada.",
        )
        if confirmation:  # Only start recording if the user clicked OK
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
        else:  # If the user clicked Cancel, you can define the behavior here
            print("User cancelled the recording")

    # ----------------------------------------------------------------STOP RECORDING
    # ----------------------------------------------------------------

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
        caseChoice = None,  # New parameter
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

            # Filter out 'sqlite_sequence' and get the desired table name
            desired_table_name = next(
                (name for name in table_names if name != "sqlite_sequence"), tableName
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

    # ----------------------------------------------------------------EXCLUIR - SQLITE_SEQUENCY TABLE
    def get_target_table_name(self, engine):
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        for name in table_names:
            if name != "sqlite_sequence":
                return name
        return None  # Se não encontrar nenhuma tabela que não seja 'sqlite_sequence'

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

            # Filtrar a tabela "sqlite_sequence"
            return [name for name in table_names if name != "sqlite_sequence"]

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
    # Check the flag and show messagebox after the webview starts


# Start the listener in a new thread
listener_thread = threading.Thread(target=listener_instance.start_listener, daemon=True)
listener_thread.start()

try:
    start_app()
except Exception as e:
    print(f"An error occurred: {e}")

listener_thread.join()
