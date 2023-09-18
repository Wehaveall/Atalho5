import keyboard  # Replacing pynput


from collections import defaultdict
from threading import Event
import pyautogui
from src.database.data_connect import lookup_word_in_all_databases

import pyperclip  # We add this import for clipboard manipulation
from src.utils import number_utils
import time
import logging


import html_clipboard


from collections import deque
import platform


import time
import re


def move_cursor_to_last_word(self):
    # Move cursor to the start of the last word without going to the end of the line
    pyautogui.hotkey("ctrl", "left")


def get_last_word_in_MS_Word():
    if platform.system() == "Windows":
        import win32com.client

        word = win32com.client.Dispatch("Word.Application")
        doc = word.ActiveDocument
        content = doc.Content.Text
        words = content.split()
        if words:
            return words[-1]
        else:
            return None
    elif platform.system() == "Darwin":  # macOS
        # Code for Mac
        print("This function is not supported on macOS")
        return None
    else:
        print("Unsupported OS")
        return None


# Setup logging - DISABLED TO CHECK PEFORMANCE
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def format_article(article, newlines=1):
    # Replacing other delimiters
    delimiters = ["*", "#", "%", "@", "$"]
    for delimiter in delimiters:
        article = article.replace(delimiter, "\n")

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
                new_article[:first_art_index] + "\n" + new_article[first_art_index:]
            )

    return new_article


class KeyListener:
    
    def __init__(self, api):  # Adicione um parâmetro window com valor padrão None
       
        keyboard.on_press(lambda e: self.on_key_press(e))
        keyboard.on_release(lambda e: self.on_key_release(e))

        self.last_word = ""  # Initialize last_word
        self.word_buffer = deque([], maxlen=5)  # Initialize with an empty deque

        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        self.winkey_pressed = False

        self.api = api

        self.key_to_str_map = {
            "Key.space": "space",
            "Key.enter": "enter",
            # Add more if needed
        }

        self.requires_delimiter = None
        self.delimiters = None

        self.accent = False
        self.last_key = None
        self.typed_keys = ""

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
            ]
        )

        self.resetting_keys = set(["space"])

    stop_event = Event()  # Renamed from stop_listener to stop_event

    def set_silent_mode(self, value):
        self.silent_mode = value

    def startRecordingMacro(self):
        self.isRecordingMacro = True

    def stopRecordingMacro(self):
        self.isRecordingMacro = False
        self.typed_keys = ""  # Add this line

    # ----------------------------------------------------------------

    def fix_double_caps(self, text):
        # Define a regex pattern to match the word with the first two letters capitalized
        pattern = r"[A-Z]{2}[a-zA-Z]*"  # Removed \b

        # Get the last word from self.last_word
        last_word = self.last_word
        print(f"Last word: {last_word}")  # Debugging line

        # Check if the last word matches the pattern
        if re.match(pattern, last_word):
            # Convert the last word to title case with only the first letter capitalized
            converted_word = last_word[0].upper() + last_word[1:].lower()
            print(f"Converted word: {converted_word}")  # Debugging line

            keyboard.unhook()
            # Clear previously typed keys
            pyautogui.hotkey("ctrl", "shiftleft", "shiftright", "left")
            pyautogui.press("backspace")
            pyperclip.copy(converted_word)

            pyautogui.hotkey("ctrl", "v")

            pyautogui.press("space")
            self.press_hook = keyboard.on_press(lambda e: self.on_key_press(e))

    # ----------------------------------------------------------------

    def paste_expansion(self, expansion, format_value):
        keyboard.unhook_all()  # Stop listening for keys - PARA CTRL V----------------------------------------------------------------

        # Clear previously typed keys
        pyautogui.hotkey("ctrl", "shiftleft", "shiftright", "left")
        pyautogui.press("backspace")

        if expansion is not None:
            format_value = int(format_value)

            if format_value == 0:
                pyperclip.copy(expansion)
                print("Debug: Using REGULAR clipboard.")
            else:
                dirty_HTML = expansion  # Your variable
                html_clipboard.PutHtml(dirty_HTML)  # Your logic
                print("Debug: Using HTML clipboard.")

            # Now paste

            pyautogui.hotkey("ctrl", "v")

        self.typed_keys = ""
        self.last_sequence = ""  # Clear last_sequence after expansion
        self.just_expanded_with = None
        
        #Restarting hook
        self.press_hook = keyboard.on_press(lambda e: self.on_key_press(e))
        self.release_hook = keyboard.on_release(lambda e: self.on_key_release(e))
        

    # ----------------------------------------------------------------Handle Accents

    def handle_accents(self, key_char):
        if key_char in self.accents:
            self.accent = key_char
        elif self.accent:
            combination = self.accent + key_char
            accented_char = self.accent_mapping.get(combination, "")
            if accented_char:
                self.typed_keys += accented_char
                self.last_sequence += accented_char  # Update last_sequence here
            self.accent = None
        else:
            self.typed_keys += key_char
            self.last_sequence += key_char  # Update last_sequence here

    # -------------------------------------------------------------------------

    def lookup_and_expand(self, sequence):
        # Suffixes
        hardcoded_suffixes = {
            "çao": ("ção", r"(?<![ã])\bçao\b"),  # updated regex
            "mn": ("mento", r".mn"),
            "ao": ("ão", r".ao"),
            # Add more here
        }

        for i in range(len(sequence) - 1, -1, -1):
            suffix = sequence[i:]

            if suffix in hardcoded_suffixes:
                expansion, regex_pattern = hardcoded_suffixes[suffix]
                if re.search(regex_pattern, sequence):
                    prefix = sequence[:i]
                    expansion = prefix + expansion  # <-- This line is corrected
                    self.paste_expansion(expansion, format_value=0)
                    return

        try:
            (
                expansion,
                format_value,
                self.requires_delimiter,
                self.delimiters,
            ) = lookup_word_in_all_databases(sequence)

        except ValueError:
            print("Not enough values returned from lookup")
            expansion = format_value = self.requires_delimiter = self.delimiters = None

        if self.requires_delimiter == "yes":
            delimiter_list = [item.strip() for item in self.delimiters.split(",")]
            key_str = self.key_to_str_map.get(str(self.last_key), str(self.last_key))
            if key_str in delimiter_list:
                if expansion is not None:
                    self.paste_expansion(expansion, format_value=format_value)
                    self.typed_keys = ""

        elif self.requires_delimiter == "no":
            if expansion is not None:
                self.paste_expansion(expansion, format_value=format_value)
                self.typed_keys = ""

    # ----------------------------------------------------------------

    # def on_key_press(self, event):
    #     key = event.name  # Define 'key' first before using it
    #     print(f"Key pressed: {key}")  # Debugging
    #     if key == "shift":
    #         self.shift_pressed = True

    ################################################################
    ################################################################

    def on_key_press(self, event):
        print(
            "on_key_release called"
        )  # Debugging: Check if the method is called at all

        key = event.name  # Get the key name directly
        print(f"Key released: {key}")  # Debugging

        # Initialize variables to None at the start of the function
        expansion = None
        format_value = None
        self.requires_delimiter = None
        self.delimiters = None

        start_time = time.time()

        # Initialize self.last_sequence if not already done
        if not hasattr(self, "last_sequence"):
            self.last_sequence = ""

        if (
            self.ctrl_pressed
            or self.shift_pressed
            or self.alt_pressed
            or self.winkey_pressed
        ):
            return

        # CTRL
        if key == "ctrl":
            self.ctrl_pressed = False

        # Shift KEY
        elif key == "shift":
            self.shift_pressed = False

        # ALT
        elif key == "alt":
            self.alt_pressed = False

        # WINKEY
        elif key == "cmd":
            self.winkey_pressed = False

        # Ignore 'enter' when self.typed_keys is empty
        if key == "enter" or (key == "space" and not self.typed_keys):
            return

        if key not in self.omitted_keys:
            if self.shift_pressed:
                char = key.upper()  # Convert to upper case if Shift is pressed
                self.shift_pressed = False  # Reset the flag immediately after use
            else:
                char = key

            self.handle_accents(char)  # Handle accents

            print(f"Self Typed Keys:__________ {self.typed_keys}")
            print(f"Last Sequence:____________ {self.last_sequence}")

        else:  # Key is in omitted_keys
            if key == "backspace":
                self.typed_keys = self.typed_keys[:-1]
                self.last_sequence = self.last_sequence[:-1]  # Update last_sequence

            elif key == "space":
                self.typed_keys += " "
                self.last_sequence = ""  # Clear last_sequence
                last_word = (
                    self.typed_keys.split()[-1] if self.typed_keys.split() else ""
                )
                self.last_word = last_word
                self.word_buffer.append(last_word)
                print(f"Debug: last_word after assignment = {self.last_word}")
                print(f"Word Buffer Before fix_double_caps: {list(self.word_buffer)}")
                self.fix_double_caps(last_word)

        try:
            self.last_key = key

            if key not in self.omitted_keys:
                self.lookup_and_expand(self.last_sequence)
            else:
                if key == "space":
                    last_word = (
                        self.typed_keys.split()[-1] if self.typed_keys.split() else ""
                    )
                    self.lookup_and_expand(last_word)

            if self.stop_event.is_set():
                return False

        except Exception as e:
            logging.error(f"Error in on_key_release: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"on_key_release processing took {elapsed_time:.2f} seconds")

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------


# def stop_keyboard_listener(listener):
#    listener.stop_listener()  # Remove the second argument, pynput_listener
