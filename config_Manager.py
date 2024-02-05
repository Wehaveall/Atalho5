import json
import logging
import os


class ConfigManager:
    _instance = None
    checkBoxStates = {}  # Class variable to hold the checkBox states

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance



    @classmethod
    def save_checkBox_states(cls, checkBoxStates):
        try:
            with open("checkBox_states.json", "w", encoding="utf-8") as f:
                json.dump(checkBoxStates, f, ensure_ascii=False)
            print("CheckBox states saved successfully.")
        except TypeError as e:
            logging.error(f"JSON serialization error in save_checkBox_states: {e}")
        except Exception as e:
            logging.error(f"Error saving checkBox states: {e}")    



    @classmethod
    def load_checkBox_states(cls):
        filePath = "checkBox_states.json"
        try:
            if os.path.exists(filePath):
                with open(filePath, "r", encoding="utf-8") as f:
                    cls.checkBoxStates = json.load(f)
                    print("Loaded checkBoxStates:", cls.checkBoxStates)  # Debugging line to print loaded states
                    print("File exists")
            else:
                print(f"{filePath} not found. Initializing empty checkbox states.")
                cls.checkBoxStates = {}
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error in load_checkBox_states: {e}")
            cls.checkBoxStates = {}
