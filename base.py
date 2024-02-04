# Standard Library Imports
from collections import deque
from ctypes import windll, Structure, c_long, byref
from functools import partial
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
import pygetwindow as gw
from screeninfo import get_monitors
from sqlalchemy import create_engine, MetaData, Table, select, update, inspect
from sqlalchemy.orm import Session
import webview

# Custom Module Imports

from popup_multiple_expansions import create_popup

from listener import KeyListener
from src.database.data_connect import (
    get_database_path,
    get_db_files_in_directory,
    load_db_into_memory,
    save_db_from_memory,
    lookup_word_in_all_databases,
)
from src.utils import number_utils

from suffix_accents_utils import *


################################################################################################################


# Global Variable Initialization


#################################################################################################################


state_lock = Lock()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


## Constants
WINDOW_TITLE = "Atalho"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global Variables
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
stop_threads = threading.Event()
state_lock = Lock()
engines = {}


# Utility Classes
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
##--------------------------------------------------------------------------


class Api:
    # Initialize API class variables
    # Used in: main.py
    def __init__(self):

        self.key_listener_instance = None
        self.is_maximized = False
        self.is_window_open = True
        self.is_recording = False
        self.events = []
        self.last_event_time = None

    def update_suffix_json_api(self, lang, pattern, is_enabled):
        update_suffix_json(lang, pattern, is_enabled)

        # Refresh the in-memory suffix patterns (if needed)
        self.suffix_patterns = load_suffix_data()  

        # Update suffix_patterns in KeyListener
        self.key_listener_instance.update_suffix_patterns(self.suffix_patterns)

    def get_initial_states(self):
        return self.load_all_states()

    # Triggered when the window is closed
    # Used in: main.py
    def on_closed(self):
        print("on_closed triggered")
        stop_threads.set()

    #######################################################################
    # Get all recorded events with intervals
    # Used in: main.py
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

    ###############################################################

    # Clear all recorded events
    # Used in: main.py
    def clear_events(self):
        self.events = []

    # ---------------------------------------------------------------- DATABASE  -----------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------------------
    # Save changes to the database
    # Used in: main.py and invoked from JavaScript
    def save_changes(self,groupName,databaseName,tableName,indexValue,shortcut,newContent,formatValue,label,caseChoice=None):

        # Explicit boolean check
        format_value_for_db = 1 if formatValue is True else 0

        # Get the engine for the specified database path
        database_path = get_database_path(groupName, databaseName)
        engine = get_engine(database_path)
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
                "shortcut": shortcut,  # Re-added shortcut
                
            }

            print(f"Debug - New Content: {newContent}")

            # If newContent is provided, update the expansion column
            if newContent:
                update_values["expansion"] = newContent

            # If label is provided, update the label column
            if label:
                update_values["label"] = label

            # Update statement based on indexValue
            stmt = (
            update(table)
            .where(table.c.id == indexValue)  # Using indexValue for update
            .values(**update_values)
            );

            # Debug: Print the statement and other variables
            print(f"Executing statement: {stmt}")
            print(f"Update values: {update_values}")
            print(f"Index value: {indexValue}")

            # Execute the update statement
            session.execute(stmt)
            session.commit()

            # Notify JavaScript to invalidate the cache after updating the database
            self.window.evaluate_js(
                'invalidateCacheEntry("{groupName}", "{databaseName}", "{tableName}")'.format(
                    groupName=groupName, databaseName=databaseName, tableName=tableName
                )
            )

    ##################################################################

    # Get all database names
    # Used in: main.py and invoked from JavaScript
    def get_database_names(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        groups_dir = os.path.join(base_dir, "groups")
        database_files = glob.glob(os.path.join(groups_dir, "*.db"))
        database_names = [
            os.path.splitext(os.path.basename(db_file))[0] for db_file in database_files
        ]

        return database_names

    ################################################################

    # Get all .db files in all subdirectories
    # Used in: main.py and invoked from JavaScript
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

            # Type checking and logging
            if not all(isinstance(item, (int, float, str)) for item in db_files):
                logging.error(f"db_files contains non-serializable types: {db_files}")
            if not isinstance(directory_name, (int, float, str)):
                logging.error(f"directory_name is of non-serializable type: {directory_name}")

            # Encode the directory name and .db files as JSON
            try:
                encoded_directory = json.dumps(directory_name)
                encoded_db_files = json.dumps(db_files)
            except TypeError as e:
                logging.error(f"JSON serialization error: {e}")
                continue  # Skip this iteration if serialization fails

            # Call createCollapsible in JavaScript for this directory and its .db files
            self.window.evaluate_js(
                f"createCollapsible({encoded_directory}, {encoded_db_files});"
            )

        return all_db_files
    # ----------------------------------------------------------------EXCLUIR - SQLITE_SEQUENCY AND CONFIG TABLE

    # Get the target table name from the database
    # Used in: This API class (self.get_data)
    def get_target_table_name(self, engine):
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        for name in table_names:
            if name not in ["sqlite_sequence", "config"]:
                return name
        return None  # If no table is found other than 'sqlite_sequence' and 'config'

    # -------------------------------------------------------------------

    # Fetch data from the database
    # Used in: main.py and invoked from JavaScript

    def get_data(self, groupName, databaseName, tableName):
        try:
            # Obter o caminho do banco de dados
            database_path = get_database_path(groupName, databaseName)

            # Usar get_engine para obter uma instância de engine
            engine = get_engine(database_path)

            # Se tableName é None, obtenha o nome da tabela que não é 'sqlite_sequence'
            if tableName is None:
                tableName = self.get_target_table_name(engine)
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
    # Get table names from the database
    # Used in: main.py and invoked from JavaScript

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

    # ----------------------------------------------------------------LANGUAGE----------------------------------------------------------------
    # Load translations from the languages.json file
    # Used in: main.py

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

    # ----------------------------------------------------------------------------------------------------------------------------------------
    # Load the current language setting
    # Used in: This API class (self.load_translations)

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

    # ----------------------------------------------------------------------------------------------------------------------------------------
    # Change the current language setting
    # Used in: main.py and invoked from JavaScript

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

    # -------------------------------------------------------------------------STATES-------------------------------------------------------------
    # Load all saved states from the state.json file
    # Used in: main.py
    def load_all_states(self):
        if not os.path.exists("state.json"):
            return {}
        with state_lock:
            with open("state.json", "r") as file:
                data = json.load(file)
                return data

    # Save all states to the state.json file
    # Used in: main.py

    def save_all_states(self, states):
        with state_lock:
            try:
                with open("state.json", "w") as file:
                    json.dump(states, file)
                    print("Updated")
            except TypeError as e:
                logging.error(f"JSON serialization error in save_all_states: {e}")

    # Save checkbox states to the checkBox_states.json file
    # Used in: main.py and invoked from JavaScript

    def save_checkBox_states(self, checkBoxStates):
        try:
            with open("checkBox_states.json", "w", encoding="utf-8") as f:
                json.dump(checkBoxStates, f, ensure_ascii=False)
        except TypeError as e:
            logging.error(f"JSON serialization error in save_checkBox_states: {e}")

    # Load checkbox states from the checkBox_states.json file
    # Used in: main.py
    def load_checkBox_states(self):
        print("Loading Checkbox States")
        filePath = os.path.join(os.path.dirname(__file__), "checkBox_states.json")
        active_databases = {}

        try:
            if os.path.exists(filePath):
                with open(filePath, "r", encoding="utf-8") as f:
                    checkBoxStates = json.load(f)
                    base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "database", "groups"))

                    for db_key, isChecked in checkBoxStates.items():
                        if isChecked:
                            # Splitting the db_key to get group and database name
                            group, dbName = db_key.split('|', 1)
                            # Construct the full path without trying to replace backslashes
                            db_full_path = os.path.join(base_directory, group, f"{dbName}.db")

                            if os.path.exists(db_full_path):
                                active_databases[db_key] = db_full_path
                            else:
                                print(f"Database marked as active not found: {db_full_path}")

            else:
                print(f"{filePath} not found. Using empty checkbox states.")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error in loading checkBox states: {e}")

        print(f"{active_databases} ACTIVE")
        return active_databases

    # -------------------------------------------------------------------------CREATE WINDOW

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

    # Call the load_handler after a short delay
    # Used in: This API class (self.create_and_position_window)

    def call_load_handler_after_delay(self):
        time.sleep(0.5)
        load_handler(self.window)


# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO)


#########------------------------------


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


###-------------------------------------------------------------START APP
# stop_threads = threading.Event()


def start_app(tk_queue):
    
    # Create an instance of Api class
    api_instance = Api()
    # Create an instance of KeyListener class and pass the Api instance to it
    key_listener_instance = KeyListener(api_instance, tk_queue)
    # Now, api_instance.key_listener_instance points to key_listener_instance
    # and key_listener_instance.api points to api_instance
    

    # -------------------------------------------------------------------------------------Start Pop-Up Thread
    # Initialize Popup Thread
    popup_thread = threading.Thread(target=create_popup,  # Note: This should be the create_popup from popup_manager.py
        args=(tk_queue, key_listener_instance, stop_threads),  # Added stop_threads here
        name="Pop-Up Thread",
    )
    popup_thread.daemon = True
    popup_thread.start()

    # --------------------------------------------------------------------------------------Start Key Listener Thread
    key_listener_thread = threading.Thread(
        target=keyboard_listener,
        args=(key_listener_instance,),
    )

    key_listener_thread.daemon = True  # Set daemon status
    key_listener_thread.start()
    # Pass the key_listener_instance to create_popup

    # threading.Thread(target=create_popup, args=(tk_queue, key_listener_instance)).start()
    print("Starting Listener from Main.py")  # Existing line
    main_window = api_instance.create_and_position_window()  # Existing line
    main_window.events.closed += api_instance.on_closed
   
   
   
    #--------------------------------------------START
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
