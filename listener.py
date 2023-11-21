# Standard Libraries
from collections import defaultdict, deque
from functools import partial
from threading import Event
import json
import logging
import configparser
import re
import time
from datetime import datetime  # New import for handling dates
from pywinauto import Desktop


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re

# Windows libraries

import ctypes

# Third-Party Libraries
import html_clipboard
import keyboard  # Replacing pynput
import pyautogui
import pyperclip  # Added for clipboard manipulation

# Project-Specific Libraries
from src.database.data_connect import lookup_word_in_all_databases
from src.utils import number_utils
from suffix_accents_utils import *
import identifier

################################################################ - NATURAL TRAINIG LANGUAGE
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.util import ngrams
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

########################################################################################################

# Setup logging - DISABLE TO CHECK PEFORMANCE
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


######################################################    KEYLISTENER    ###############################################################
########################################################################################################################################
class KeyListener:
    def __init__(
        self, api_instance, tk_queue=None
    ):  # Add tk_queue as an optional parameter
        # Carrega o resultado da função load_suffix_data que está dentro do arquivo suffix_accents_utils.py na self
        # variável suffix_patterns
        # def get_current_suffix_patterns():
        #   return load_suffix_data()

        self.word_at_caret = ""
        self.current_focused_element = None
        self.suffix_patterns = get_current_suffix_patterns()

        self.expansion_triggered_by_enter = False
        self.tk_queue = tk_queue  # Assign it to an instance variable
        self.expansions_list = []  # Define the expansions_list
        self.programmatically_typing = False  # Initialize the flag here
        self.last_word = ""  # Initialize last_word
        self.word_buffer = deque([], maxlen=500)  # Initialize with an empty deque
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        self.winkey_pressed = False

        self.api = api_instance
        self.api.key_listener_instance = (
            self  # Update the Api instance to point to this KeyListener instance
        )

        self.key_to_str_map = {
            "Key.space": "space",
            "Key.enter": "enter",
            # Add more if needed
        }

        self.requires_delimiter = None
        self.delimiters = None
        self.accent = False
        self.last_key = None
        self.typed_keys = """"""

        # Added this line to store the pynput listener
        # self.pynput_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)

        self.accent_mapping = defaultdict(
            lambda: "",
            {
                "~a": "ã",
                "~A": "Ã",
                "~o": "õ",
                "~O": "Õ",
                "~n": "ñ",
                "~N": "Ñ",
                "´a": "á",
                "´A": "Á",
                "´e": "é",
                "´E": "É",
                "´i": "í",
                "´I": "Í",
                "´o": "ó",
                "´O": "Ó",
                "´u": "ú",
                "´U": "Ú",
                "`a": "à",
                "`A": "À",
                "`e": "è",
                "`E": "È",
                "`i": "ì",
                "`I": "Ì",
                "`o": "ò",
                "`O": "Ò",
                "`u": "ù",
                "`U": "Ù",
                "^a": "â",
                "^A": "Â",
                "^e": "ê",
                "^E": "Ê",
                "^i": "î",
                "^I": "Î",
                "^o": "ô",
                "^O": "Ô",
                "^u": "û",
                "^U": "Û",
            },
        )

        self.accents = set(["~", "´", "`", "^"])

        self.omitted_keys = set(
            [
                "esc",
                "shift",
                "ctrl",
                "alt",
                "cmd",
                "f1",
                "f2",
                "f3",
                "f4",
                "f5",
                "f6",
                "f7",
                "f8",
                "f9",
                "f10",
                "f11",
                "f12",
                "page up",
                "page down",
                "home",
                "end",
                "delete",
                "insert",
                "up",
                "down",
                "left",
                "right",
                "backspace",
                "print screen",
                "scroll lock",
                "pause",
                "space",
                "caps lock",
                "tab",
                "enter",
                "num lock",
                "right ctrl",
                "left ctrl",
                "left shift",
                "right shift",
            ]
        )

        self.resetting_keys = set(["space"])

        # Reading JSON file to get the suffix setting
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.use_auto_suffixes = config.get(
                    "use_auto_suffixes", True
                )  # Default to True if not present
        except FileNotFoundError:
            self.use_auto_suffixes = True  # Default to True if config file is not found

    ###################################################################### FUNCTIONS
    # TO DO - newline must be configurable in the GUI

    #!!!!!!!!! O Status do numlock influencia muito na ações da library Keyboard. Dependendo se on ou off, muitas teclas
    # não vao funcionar corretamente.

    def update_suffix_patterns(self, new_patterns):
        self.suffix_patterns = new_patterns

    def format_article(self, article, newlines=2):
        # Replacing other delimiters
        delimiters = ["*", "#", "%", "@", "$"]
        for delimiter in delimiters:
            article = article.replace(delimiter, "\n" * newlines)

        # Handling "++" delimiter
        plus_sections = article.split("++")
        new_article = plus_sections[0]  # Keep the first section as it is

        if len(plus_sections) > 1:  # Only proceed if "++" exists in the article
            counter = 0  # Counter to keep track of "++" occurrences after the first one
            for section in plus_sections[1:]:
                # If counter is zero, simply remove the "++"
                if counter == 0:
                    new_article += section
                # If counter is more than zero, add newline before "Art."
                else:
                    art_split = section.split(
                        "Art.", 1
                    )  # Split by the first occurrence of "Art."
                    if len(art_split) > 1:
                        new_article += "\n" * newlines + "Art.".join(art_split)
                        counter = 0  # Reset the counter
                    else:
                        new_article += "\n" * newlines + section

                # Increment the counter after the first "++"
                counter += 1

            # Add a newline before the first occurrence of "Art." if "++" exists
            first_art_index = new_article.find("Art.")
            if first_art_index != -1:
                new_article = (
                    new_article[:first_art_index]
                    + "\n" * newlines
                    + new_article[first_art_index:]
                )

        return new_article

    def general_handler(self, event):
        if event.event_type == "down":
            self.on_key_press(event)
        elif event.event_type == "up":
            self.on_key_release(event)

    def stop_listener(self):
        print("Stopping Listener from Listener.py")
        try:
            # Unhook the keyboard listener
            keyboard.unhook(self.hook)
            print("Successfully unhooked the keyboard listeners.")
        except Exception as e:
            print(f"An error occurred while unhooking: {e}")

    def start_listener(self):
        print("Starting Listener from Listener.py")
        try:
            # Hook the general_handler function to listen to keyboard events
            self.hook = keyboard.hook(self.general_handler)
            print("Successfully hooked the keyboard listeners.")
        except Exception as e:
            print(f"An error occurred while hooking: {e}")

    # ----------------------------------------GRAMMAR AND ORTOGRAPH ---------------

    def capture_ngrams_and_collocations(self):
        # Tokenize the accumulated text
        words = word_tokenize(self.typed_keys)

        # Generate bigrams
        bigrams = list(ngrams(words, 2))

        # Find collocations using bigrams
        bigram_finder = BigramCollocationFinder.from_words(words)
        bigram_scored = bigram_finder.score_ngrams(BigramAssocMeasures.raw_freq)

        # Write to a JSON file
        with open("bigram_data.json", "w") as f:
            json.dump(bigram_scored, f)

        return bigrams, bigram_scored

    # -------------------------------------------DOUBLE CAPS--------------------------
    def fix_double_caps(self, word_at_caret):
        pattern = r"\b[A-Z]{2}[a-zA-Z]*\b"  # Removed \b

        if re.match(pattern, word_at_caret):
            converted_word = word_at_caret[0].upper() + word_at_caret[1:].lower()
            print(f"Converted word: {converted_word}")  # Debugging line

            keyboard.unhook_all()

            # Set flag to indicate programmatic typing
            self.programmatically_typing = True


            # Check if numlock is on -----------------------------------------------------------
            def is_numlock_on():
                # GetKeyState function retrieves the status of the specified key
                # VK_NUMLOCK (0x90) is the virtual-key code for the NumLock key
                return ctypes.windll.user32.GetKeyState(0x90) != 0

            def toggle_numlock():
                # Toggle NumLock state
                keyboard.press_and_release("num lock")

            # Example usage
            if is_numlock_on():
                print("NumLock is ON")
                state = True
                toggle_numlock()

            else:
                print("NumLock is OFF")
            #-------------------------------------------------------------------------------------
            
            
            # Clear previously typed keys
            keyboard.press("ctrl")
            keyboard.press("shift")
            time.sleep(0.05)
            keyboard.press_and_release("left arrow")
            keyboard.release("shift")
            keyboard.release("ctrl")
            keyboard.press_and_release("backspace")

            pyperclip.copy(converted_word)

            time.sleep(0.05)
            keyboard.press_and_release("ctrl+v")
            time.sleep(0.05)
            # Insert a space
            keyboard.write(" ")
            time.sleep(0.05)

            # Debugging line to check the value of self.typed_keys before modification
            print(f"Before: {self.typed_keys}")

            # Update the last word and the typed keys
            if self.typed_keys.endswith(word_at_caret + " "):
                self.typed_keys = (
                    self.typed_keys[: -len(word_at_caret) - 1] + converted_word + " "
                )

            elif self.typed_keys.endswith(word_at_caret):
                self.typed_keys = (
                    self.typed_keys[: -len(word_at_caret)] + converted_word + " "
                )

            # Debugging line to check the value of self.typed_keys after modification
            print(f"After: {self.typed_keys}")

            if state == True:
                toggle_numlock()
            
            # Reset the flag
            self.programmatically_typing = False

            # Restarting hook
            self.press_hook = keyboard.on_press(lambda e: self.on_key_press(e))
            return

    # ----------------------------------------------------------------

    def paste_expansion(self, expansion, format_value):
        print(f"Debug: paste_expansion called with expansion: {expansion}, format_value: {format_value}")

        self.programmatically_typing = True  # Set the flag
        # Debug: Print before changes

        # Check if numlock is on----------------------------------------------------------
        def is_numlock_on():
            # GetKeyState function retrieves the status of the specified key
            # VK_NUMLOCK (0x90) is the virtual-key code for the NumLock key
            return ctypes.windll.user32.GetKeyState(0x90) != 0

        def toggle_numlock():
            # Toggle NumLock state
            keyboard.press_and_release("num lock")

        # Example usage
        if is_numlock_on():
            print("NumLock is ON")
            state = True
            toggle_numlock()

        else:
            state = False
            print("NumLock is OFF")

        #--------------------------------------------------------------------------------
       
        # New code: Locate %cursor% in the expansion and record its position
        cursor_position = None
        if expansion and "%CURSOR%" in expansion:
            cursor_position = expansion.index("%CURSOR%")
            expansion = expansion.replace("%CURSOR%", "")

        # Handle the Enter key triggering an expansion
        if self.expansion_triggered_by_enter:
            keyboard.press_and_release("backspace")
            self.expansion_triggered_by_enter = False  # Reset the flag

        # Clear previously typed keys
        keyboard.press("ctrl")
        keyboard.press("shift")
        keyboard.press_and_release("left arrow")
        keyboard.release("shift")
        keyboard.release("ctrl")
        time.sleep(0.1)  # Time to avoid errors
        keyboard.press_and_release("backspace")
        time.sleep(0.1)  # Time to avoid errors

        if expansion is not None:
            # Format the expansion before pasting (This is the new line)
            formatted_expansion = self.format_article(expansion, newlines=2)

            format_value = int(format_value)

            if format_value == 0:
                pyperclip.copy(
                    formatted_expansion
                )  # Modified to use formatted_expansion
                print("Debug: Using REGULAR clipboard.")
            else:
                dirty_HTML = formatted_expansion  # Modified to use formatted_expansion
                html_clipboard.PutHtml(dirty_HTML)  # Your logic
                print("Debug: Using HTML clipboard.")

            # Now paste
            keyboard.press_and_release("ctrl+v")
            time.sleep(0.01)

            # Move the mouse 1 pixel to the right (This is the new line)
            # Provisional solution because paste will only appear after mouse move
            current_x, current_y = pyautogui.position()  # Get current mouse position
            pyautogui.moveTo(
                current_x + 2, current_y
            )  # Move mouse 1 pixel to the right
            pyautogui.moveTo(
                current_x - 2, current_y
            )  # Move mouse 1 pixel to the right

            # New code: Move the cursor to the cursor_position
            if cursor_position is not None:
                # Calculate the number of characters to move the cursor backwards
                move_back_count = len(expansion) - cursor_position

                # Move the cursor back to the recorded position
                for _ in range(move_back_count):
                    keyboard.press_and_release("left arrow")

        # Update other variables
        self.typed_keys = ""

        if state == True:
            toggle_numlock()

        self.programmatically_typing = False  # Reset the flag
      

    # ----------------------------------------------------------------Handle Accents

    def handle_accents(self, key_char):
        if key_char in self.accents:
            self.accent = key_char
            return ""  # Return an empty string instead of None

        elif self.accent:
            combination = self.accent + key_char
            accented_char = self.accent_mapping.get(combination, "")

            if accented_char:
                self.typed_keys += accented_char
                self.accent = None
                return accented_char  # Return the accented character

            self.accent = None

        return key_char  # Return the original character or an empty string if key_char is None


    # -------------------------------------------------------------------------
    # Is deleting multiline previous content after expansion
    def make_selection(self, index, popup):  # Added popup as an argument
        popup.destroy()  # Destroy the popup
        time.sleep(0.05)  # Add a small delay here

        selected_expansion_data = self.expansions_list[index]
        expansion_to_paste = selected_expansion_data["expansion"]

        # Call the paste_expansion method
        self.paste_expansion(
            expansion_to_paste,
            format_value=selected_expansion_data["format_value"],
        )

        self.just_pasted_expansion = True
        self.word_at_caret = ""

        self.start_listener()
        return

    ############################################################################################################

    def create_popup(self):
        print("Entered create_popup method")  # Debugging line

        if self.tk_queue:
            self.tk_queue.put(("create_popup", self.expansions_list, self))
            print("Added to tk_queue")  # Debugging line
        else:
            print("tk_queue is None")  # Debugging line

    ##--------------------------------------------------------------------------------------------

    def lookup_and_expand(self, sequence):
        # Suffix
        # Aqui o dicionário já está carregado quando inicia a classe
        for pattern, replacement in self.suffix_patterns.items():
            match = re.search(pattern, sequence)
            if match:
                expanded_sequence = re.sub(pattern, replacement, sequence)
                self.paste_expansion(expanded_sequence, format_value=0)
                self.typed_keys = ""

                return  # Exit the function to prevent further processing

            else:
                pass
                # print("Debug - Nothing found")

        try:
            expansions_list = lookup_word_in_all_databases(sequence)
            # print(f"Debug: Type of expansions_list: {type(expansions_list)}")  # Debug print
            # print(f"Debug: All expansions found: {expansions_list}")  # Debug print
        except ValueError:
            # print("Not enough values returned from lookup1")
            return  # Exit the function if the lookup failed

        if len(expansions_list) > 1:
            self.expansions_list = expansions_list
            self.create_popup()

            if (
                not self.popup_selector.selection_made
            ):  # <-- Check if a selection was made
                self.word_at_caret = ""
                return  # Exit the function if no selection was made

        elif len(expansions_list) == 1:
            print("Debug: Single expansion detected.")  # Debug print

            # Handling the first element in the list of expansions
            expansion_data = expansions_list[0]
            expansion = expansion_data.get("expansion", None)
            format_value = expansion_data.get("format_value", None)
            self.requires_delimiter = expansion_data.get("requires_delimiter", None)
            self.delimiters = expansion_data.get("delimiters", None)

            # print(f"Debug: Expansion found for {sequence} is {expansion} with format_value {format_value}")  # Debug print

        # New code: Replace %DATE% with the current date in dd-mm-yyyy format
        if expansion and "%DATE%" in expansion:
            current_date = datetime.now().strftime("%d/%m/%Y")
            expansion = expansion.replace("%DATE%", current_date)

        key_str = self.key_to_str_map.get(str(self.last_key), str(self.last_key))

        if self.requires_delimiter == "yes":
            delimiter_list = [item.strip() for item in self.delimiters.split(",")]

            if key_str in delimiter_list:
                if expansion is not None:
                    if key_str == "enter":
                        self.expansion_triggered_by_enter = True
                    # Potentially delete the shortcut text here before pasting the expansion
                    self.paste_expansion(expansion, format_value=format_value)
                    self.typed_keys = ""

        elif self.requires_delimiter == "no":
            if expansion is not None:
                self.paste_expansion(expansion, format_value=format_value)
                self.typed_keys = ""

    ################################################################
    ################################################################

    def on_key_release(self, event):
        key = event.name  # Capture the released key's name
        # print(f"Key {key} released.")

        # Reset the state of the modifier keys if they are released
        if key == "ctrl":
            self.ctrl_pressed = False
        elif key == "shift":
            self.shift_pressed = False
        elif key == "alt":
            self.alt_pressed = False
        elif key == "cmd":  # Assuming 'cmd' is the Windows key
            self.winkey_pressed = False

    def on_key_press(self, event):
        # Initialize variables to None at the start of the function
        word_at_caret = None
        self.requires_delimiter = None
        self.delimiters = None
        char = None  # Highlighted Change

        key = event.name  # Capture the key name first
        # print(f"Key {key} pressed.")

        # Before anything, update the state of the modifier keys
        if key == "ctrl":
            self.ctrl_pressed = True

        elif key == "shift":
            self.shift_pressed = True

        elif key == "alt":
            self.alt_pressed = True

        elif key == "cmd":  # Assuming 'cmd' is the Windows key
            self.winkey_pressed = True

        # Check if we should skip processing this key press
        if (
            self.programmatically_typing
            or self.ctrl_pressed
            or self.alt_pressed
            or self.winkey_pressed
        ):
            return

        # Handle keypress for character keys
        if (
            key.isprintable() and not key.isspace()
        ):  # Check if key is a printable character and not a space
            # Convert to upper case if Shift is pressed, otherwise use the character as is
            char = key.upper() if self.shift_pressed else key

        # Reset the shift flag after use if it was pressed
        if self.shift_pressed:
            self.shift_pressed = False

        start_time = time.time()

        # Ignore 'space' when self.typed_keys is empty
        if key == "space" and not self.typed_keys:
            return

        if key not in self.omitted_keys:
            # Convert to upper case if Shift is pressed, otherwise use the key as it is
            char = key.upper() if self.shift_pressed else key
            self.shift_pressed = False  # Reset the shift flag after use

            # Process the character for accents or other modifications
            processed_char = self.handle_accents(char)

            # Update the self.typed_keys with the processed character
            self.typed_keys += processed_char
            print(f"Self Typed= {self.typed_keys}")

            ########################################################## IDENTIFY APP - FIELD - FULL TEXT - CARET POSITION #####################
            window_title = pyautogui.getActiveWindowTitle()
            print(window_title)
            ##

            # result = identifier.get_focused_info()  # Here we use test.main to reference the main function from test.py
            # print("Result from identifier.py:", result)

            # Fetch the word at the caret from the identifier module
            identifier_info = identifier.get_focused_info()
            word_at_caret = identifier_info.get("word_at_caret", "")
            print("Result from identifier.py:", identifier_info, word_at_caret)

            ##################################################################################################################################

            # print(f"Self Typed Keys:__ {self.typed_keys}")
            # print(f"Last Sequence:__1 {self.last_sequence}")

        else:  # Key is in omitted_keys
            if key == "backspace":
                self.typed_keys = self.typed_keys[:-1]

            elif key == "space":
                # Fetch the word at the caret from the identifier module
                identifier_info = identifier.get_focused_info()
                word_at_caret = identifier_info.get("word_at_caret", "")
                print("Result from identifier.py:", identifier_info, word_at_caret)

                # Here, we check if the word at the caret matches the pattern for double caps
                self.fix_double_caps(word_at_caret)

                # Continue processing the space key as normal
                self.typed_keys += " "

            # ---------------------------------------WORDS--------------------------------
            # Tokenize the sentence into words
            # words_from_multi_line = word_tokenize(self.multi_line_string)

            # Get the last word only if the list is not empty
            # self.last_word = words_from_multi_line[-1] if words_from_multi_line else None

            # --------------------------------------SENTENCES-----------------------------
            # Sentence Tokenization
            # sentences = sent_tokenize(self.multi_line_string)
            # last_sentence = sentences[-1] if sentences else ""
            # last_sentence = sentences[-1] if sentences else None  # Highlighted Change

            # ---------------------------------------ENTITIES--------------------------------
            # Tokenization
            # tokens = word_tokenize(self.multi_line_string)  # Make sure self.typed_keys is a string
            # tags = pos_tag(tokens)
            # entities = ne_chunk(tags)

            # ---------------------------------------COLLECT DATA
            # Call the new method here
            # self.capture_ngrams_and_collocations()

            # --------------------------------PRINTS--------------------------------

            # print(f"Entities = {entities}")
            # print(f"Sentence List= {sentences}")
            # print(f"Last Sentence = {last_sentence}")
            # print(f"Words List= {words_from_multi_line}")

        try:
            self.last_key = key

            if key not in self.omitted_keys:
                if (key != "backspace"):  # Add condition to skip "backspace" triggering shortcuts
                    self.lookup_and_expand(word_at_caret)  # Use word_at_caret instead of self.last_sequence

            else:
                # Initialize delimiter_list at the start of your function
                delimiter_list = (
                    self.delimiters.split(",")
                    if self.delimiters
                    else ["space", "enter"]
                )

                if key in delimiter_list:
                    if (key != "backspace"):  # Add condition to skip "backspace" triggering shortcuts
                        # Tokenize the sentence into words
                        words = word_tokenize(self.typed_keys)
                        # Get the last word only if words list is not empty
                        last_word = words[-1] if words else None
                        if word_at_caret:
                            self.lookup_and_expand(word_at_caret)
                            word_at_caret = ""  # Clear word_at_caret after successful expansion

        except Exception as e:
            pass
            # logging.error(f"Error in on_key_release: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"on_key_release processing took {elapsed_time:.2f} seconds")

    # ----------------------------------------------------------------
