from pynput import keyboard
from collections import defaultdict
from threading import Event
import pyautogui
from src.database.data_connect import lookup_word_in_all_databases
import pyperclip  # We add this import for clipboard manipulation
from src.utils import number_utils
import time
import logging


from bs4 import BeautifulSoup
import html_clipboard


from collections import deque
import platform


import time
from pynput import keyboard
import re
import win32clipboard

suffix_to_regex = {
    "cao": ".cao",  # should only expand when following another character
    "other_suffix": "other_pattern"
    # ... add more here
}


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


# Setup logging
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
        self.pynput_listener = None
        self.silent_mode = False
        self.isRecordingMacro = False
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
                keyboard.Key.esc,
                keyboard.Key.shift,
                keyboard.Key.shift_r,
                keyboard.Key.ctrl_l,
                keyboard.Key.ctrl_r,
                keyboard.Key.alt_l,
                keyboard.Key.alt_r,
                keyboard.Key.alt_gr,
                keyboard.Key.cmd,
                keyboard.Key.f1,
                keyboard.Key.f2,
                keyboard.Key.f3,
                keyboard.Key.f4,
                keyboard.Key.f5,
                keyboard.Key.f6,
                keyboard.Key.f7,
                keyboard.Key.f8,
                keyboard.Key.f9,
                keyboard.Key.f10,
                keyboard.Key.f11,
                keyboard.Key.f12,
                keyboard.Key.page_up,
                keyboard.Key.page_down,
                keyboard.Key.home,
                keyboard.Key.end,
                keyboard.Key.delete,
                keyboard.Key.insert,
                keyboard.Key.up,
                keyboard.Key.down,
                keyboard.Key.left,
                keyboard.Key.right,
                keyboard.Key.backspace,
                keyboard.Key.print_screen,
                keyboard.Key.scroll_lock,
                keyboard.Key.pause,
                keyboard.Key.space,
                keyboard.Key.caps_lock,
                keyboard.Key.tab,
                keyboard.Key.enter,
                keyboard.Key.num_lock,
            ]
        )
        self.resetting_keys = set([keyboard.Key.space])

    stop_event = Event()  # Renamed from stop_listener to stop_event

    def set_silent_mode(self, value):
        self.silent_mode = value

    def startRecordingMacro(self):
        self.isRecordingMacro = True

    def stopRecordingMacro(self):
        self.isRecordingMacro = False
        self.typed_keys = ""  # Add this line

    # ----------------------------------------------------------------

    @staticmethod
    def get_suffix_pattern_from_database(suffix):
        return suffix_to_regex.get(suffix)

    # ----------------------------------------------------------------

    def paste_expansion(self, expansion, format_value):
        self.pynput_listener.stop()  # Stop listening for keys

        # Debug statements

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
        self.start_listener()  # Start listening for keys again

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

    def on_key_release(self, key):
        # Initialize variables to None at the start of the function
        expansion = None
        format_value = None
        self.requires_delimiter = None
        self.delimiters = None
        # Inicia KeyChar
        # key_char = key.char if hasattr(key, 'char') and key.char else ""

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

        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            self.shift_pressed = False
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.alt_pressed = False
        elif key == keyboard.Key.cmd:
            self.winkey_pressed = False

        # Ignora enter quando não há  nada em self_typed_keys
        if (
            key == keyboard.Key.enter
            or key == keyboard.Key.space
            and not self.typed_keys
        ):
            return

        if key not in self.omitted_keys:
            if hasattr(key, "char") and key.char:
                self.handle_accents(
                    key.char
                )  # Handle accents lida tanto com self_typed ou last-sequence

                print(f"Self Typed Keys:__________ {self.typed_keys}")
                print(f"Last Sequence:____________ {self.last_sequence}")  # Debug

        else:  # Key is in omitted_keys
            if key == keyboard.Key.backspace:
                self.typed_keys = self.typed_keys[:-1]
                self.last_sequence = self.last_sequence[:-1]  # Update last_sequence

            elif key == keyboard.Key.space:
                self.typed_keys += " "
                self.last_sequence = ""  # Clear last_sequence
                last_word = (
                    self.typed_keys.split()[-1] if self.typed_keys.split() else ""
                )
                self.word_buffer.append(
                    last_word
                )  # Add the last word to the word_buffer deque
                print(f"Last Word:----------- {last_word}")
                print(
                    f"Word Buffer:---------- {list(self.word_buffer)}"
                )  # Print the current word buffer

        try:
            self.last_key = key  # Add this line to update the last key pressed

            # Check silent mode is enabled
            if self.isRecordingMacro:
                return

            if self.silent_mode:
                return

            if key in self.omitted_keys and self.api.is_recording:
                return

            if key not in self.omitted_keys:
                self.lookup_and_expand(
                    self.last_sequence
                )  # New line for lookup_and_expand

            else:
                if key == keyboard.Key.space:
                    last_word = (
                        self.typed_keys.split()[-1] if self.typed_keys.split() else ""
                    )
                    self.lookup_and_expand(
                        last_word
                    )  # New line for lookup_and_expand when space is pressed

            if self.stop_event.is_set():
                return False

        except Exception as e:
            logging.error(f"Error in on_key_release: {e}")
            self.restart_listener()

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"on_key_release processing took {elapsed_time:.2f} seconds")

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------

    def restart_listener(self):
        logging.info("Restarting listener...")
        self.stop_listener()
        self.start_listener()

    def start_listener(self):
        self.typed_keys = ""  # Clear the typed keys
        self.pynput_listener = keyboard.Listener(on_release=self.on_key_release)
        print("Starting GlobaL listener...")
        self.pynput_listener.start()

    def stop_listener(self):
        if self.pynput_listener is not None:
            if self.pynput_listener.running:
                print("Stopping Macro listener...")
                self.pynput_listener.stop()
                self.pynput_listener.join()
                self.pynput_listener = None
                self.typed_keys = ""  # Move this line here
            else:
                print("Listener is not running, no need to stop it.")
        else:
            print("No listener to stop.")

    def handle_accent_key(self, key_char):
        self.accent = False
        combination = self.last_key + key_char
        accented_char = self.accent_mapping[combination]

        # Add the accented character to the char_buffer
        self.char_buffer += accented_char  # Add this line

    def start(self):
        self.start_listener()  # Change self.listener.start() to self.start_listener()

    def stop(self):
        self.stop_listener()  # Change self.listener.stop() to self.stop_listener()


def stop_keyboard_listener(listener):
    listener.stop_listener()  # Remove the second argument, pynput_listener
