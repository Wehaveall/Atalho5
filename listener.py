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
import json

#######################################
######################### POP UP FOR MULTIPLE EXPANSIONS
import win32com.client
import win32gui
import win32con
import win32gui

import win32con
import tkinter as tk
from tkinter import Button
################################################################ - NATURAL TRAINIG LANGUAGE
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

##Capturing frequently occurring phrases can certainly be beneficial for suggesting hotstrings or automating text input.
# To achieve this, you can use NLTK's functionality for finding collocations and extracting n-grams.
# Here's how:
# 1. N-gram Extraction
# An n-gram is a contiguous sequence of #n items (such as characters or words) from a given sample of text.
# The function ngrams from the nltk.util module can help you generate n-grams.

# 2. Collocation Finding

# Collocations are sequences of words that appear together more often than would be expected by chance.
# The BigramCollocationFinder and TrigramCollocationFinder classes in the nltk.collocations module can help identify these.
from nltk.util import ngrams
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
#################################################################



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


# Setup logging - DISABLE TO CHECK PEFORMANCE
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


############################################################################

class TkinterPopupSelector:
    def __init__(self, options, callback, key_listener):
        self.callback = callback
        self.key_listener = key_listener  # Store the key_listener instance

        # Stop keyboard listener
        self.key_listener.stop_listener()

        # Wait for a small period to ensure the keyboard listener has fully stopped
        time.sleep(0.1)

        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

        self.top_window = tk.Toplevel(self.root)
        self.top_window.geometry("900x700")
        self.top_window.title('Select Expansion')
        
        input_element = tk.Entry(self.top_window)
        input_element.pack()
        input_element.focus_set()  # Move focus to the input element

        for i, option in enumerate(options):
            button = tk.Button(self.top_window, text=f"{i + 1}. {option}", command=lambda i=i: self.make_selection(i))
            button.pack()

        # Attempt to bring Tkinter window to the foreground
        self.bring_window_to_foreground()

        self.root.mainloop()

    def bring_window_to_foreground(self):
        self.top_window.update_idletasks()
        hwnd = win32gui.FindWindow(None, 'Select Expansion')
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        shell.SendKeys('%')  
        win32gui.SetForegroundWindow(hwnd)
        # Send another Alt key to nullify the activation
        self.top_window.focus_force()
        

    def make_selection(self, index):
        print("Debug: make_selection called")
        
        self.callback(index)
        self.top_window.destroy()
        self.root.quit()

        # Restart keyboard listener
        self.key_listener.start_listener()


        # Add a small delay here
        time.sleep(0.1)  # You can adjust the duratio

        # Explicitly call paste_expansion here to test
        selected_expansion_data = self.key_listener.expansions_list[index]
        self.key_listener.paste_expansion(
            selected_expansion_data['expansion'],
            format_value=selected_expansion_data['format_value']
        )





########################################################################
class KeyListener:
   

    def __init__(self, api):  # Adicione um parâmetro window com valor padrão None

        self.expansions_list = []  # Define the expansions_list

        keyboard.on_press(lambda e: self.on_key_press(e))
        keyboard.on_release(lambda e: self.on_key_release(e))

        self.programmatically_typing = False  # Initialize the flag here

        self.last_word = ""  # Initialize last_word
        self.word_buffer = deque([], maxlen=50)  # Initialize with an empty deque

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
                "right ctrl",
                "left ctrl",
                "left shift",
                "right shift",
                # Add more here
            ]
        )

        self.resetting_keys = set(["space"])


    def stop_listener(self):
        keyboard.unhook_all()

    
    def start_listener(self):
        keyboard.on_press(lambda e: self.on_key_press(e))
        keyboard.on_release(lambda e: self.on_key_release(e))


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
    def fix_double_caps(self, last_word):
        
        pattern = r"\b[A-Z]{2}[a-zA-Z]*\b"  # Removed \b

        if re.match(pattern, last_word):
            converted_word = last_word[0].upper() + last_word[1:].lower()
            print(f"Converted word: {converted_word}")  # Debugging line

            keyboard.unhook_all()

            # Set flag to indicate programmatic typing
            self.programmatically_typing = True

            # Clear previously typed keys
            keyboard.press("ctrl")
            keyboard.press("shift")
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
            if self.typed_keys.endswith(last_word + " "):
                self.typed_keys = self.typed_keys[:-len(last_word) - 1] + converted_word + " "
            
            elif self.typed_keys.endswith(last_word):
                self.typed_keys = self.typed_keys[:-len(last_word)] + converted_word + " "

            # Debugging line to check the value of self.typed_keys after modification
            print(f"After: {self.typed_keys}")

            # Reset the flag
            self.programmatically_typing = False

            # Restarting hook
            self.press_hook = keyboard.on_press(lambda e: self.on_key_press(e))
            return


    # ----------------------------------------------------------------

    def paste_expansion(self, expansion, format_value):
        print(f"Debug: paste_expansion called with expansion: {expansion}, format_value: {format_value}")
        self.programmatically_typing = True  # Set the flag
        keyboard.unhook_all()  # Stop listening for keys - PARA CTRL V

        # Clear previously typed keys
        keyboard.press("ctrl")
        keyboard.press("shift")
        keyboard.press_and_release("left arrow")
        keyboard.release("shift")
        keyboard.release("ctrl")
        keyboard.press_and_release("backspace")

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
            keyboard.press_and_release("ctrl+v")

        # Restarting hook
        self.press_hook = keyboard.on_press(lambda e: self.on_key_press(e))
        self.release_hook = keyboard.on_release(lambda e: self.on_key_release(e))
        self.programmatically_typing = False  # Reset the flag

        # Remove the last incorrect word from self.typed_keys
        self.typed_keys = self.typed_keys.rstrip(self.last_word)

        # Add the corrected word
        self.typed_keys += expansion + " "

        self.last_word = expansion  # Update the last word to the new expanded word
        self.word_buffer.append(expansion)  # Add the expanded word to the buffer

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
        hardcoded_suffixes = {
            "çao": ("ção", r"(?<![ã])\bçao\b"),
            "mn": ("mento", r".mn"),
            "ao": ("ão", r".ao"),
        }

        words = word_tokenize(sequence)
        if words:
            last_word = words[-1]

        for i in range(len(last_word) - 1, -1, -1):
            suffix = last_word[i:]
            if suffix in hardcoded_suffixes:
                expansion, regex_pattern = hardcoded_suffixes[suffix]
                if re.search(regex_pattern, last_word):
                    prefix = last_word[:i]
                    expansion = prefix + expansion

                    if self.typed_keys.endswith(last_word + " "):
                        self.typed_keys = self.typed_keys[:-len(last_word) - 1]
                    elif self.typed_keys.endswith(last_word):
                        self.typed_keys = self.typed_keys[:-len(last_word)]

                    if self.word_buffer and self.word_buffer[-1] == last_word:
                        self.word_buffer.pop()

                    self.paste_expansion(expansion, format_value=0)
                    return

        expansions_list = []
        try:




            expansions_list = lookup_word_in_all_databases(sequence)
        except ValueError:
            print("Not enough values returned from lookup")

        if len(expansions_list) > 1:
            self.expansions_list = expansions_list  # Store the expansions list
            TkinterPopupSelector([exp['expansion'] for exp in expansions_list], self.callback, self)

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
    def callback(self, index):
        selected_expansion_data = self.expansions_list[index]
        print("Debug: callback called with index", index)
        self.paste_expansion(
            selected_expansion_data['expansion'],
            format_value=selected_expansion_data['format_value']
        )



    def on_key_press(self, event):
        if self.programmatically_typing:  # Skip if we are programmatically typing
            return

        print(
            "on_key_press called"
        )  # Debugging: Changed from on_key_release to on_key_press
        key = event.name
        print(
            f"Key pressed: {key}"
        )  # Debugging: Changed from Key released to Key pressed

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

            print(f"Self Typed Keys:__ {self.typed_keys}")
            print(f"Last Sequence:__ {self.last_sequence}")

        else:  # Key is in omitted_keys
            if key == "backspace":
                self.typed_keys = self.typed_keys[:-1]
                self.last_sequence = self.last_sequence[:-1]  # Update last_sequence

            elif key == "space":
                
                self.typed_keys += " "
                self.last_sequence = ""  # Clear last_sequence

                # ---------------------------------------WORDS--------------------------------
                # Tokenize the sentence into words
                words = word_tokenize(self.typed_keys)
                # Get the last word
                last_word = words[-1]

                self.fix_double_caps(last_word)  # Call fix_double_caps here
                self.lookup_and_expand(last_word)

                # --------------------------------------SENTENCES-----------------------------
                # Sentence Tokenization
                sentences = sent_tokenize(self.typed_keys)
                last_sentence = sentences[-1] if sentences else ""

                # ---------------------------------------ENTITIES--------------------------------
                # Tokenization
                tokens = word_tokenize(
                    self.typed_keys
                )  # Make sure self.typed_keys is a string
                tags = pos_tag(tokens)
                entities = ne_chunk(tags)

                # ---------------------------------------COLLECT DATA
                # Call the new method here
                self.capture_ngrams_and_collocations()

                # --------------------------------PRINTS--------------------------------
                print(f"Entities = {entities}")

                print(f"Sentence List= {sentences}")
                print(f"Last Sentence = {last_sentence}")

                print(f"Words List= {words}")
                print(f"Last Word= {last_word}")

        try:
            self.last_key = key

            if key not in self.omitted_keys:
                self.lookup_and_expand(self.last_sequence)
            else:
                if key == "space":
                    # Tokenize the sentence into words
                    words = word_tokenize(self.typed_keys)

                    # Get the last word
                    last_word = words[-1]
                    self.lookup_and_expand(last_word)

        except Exception as e:
            logging.error(f"Error in on_key_release: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"on_key_release processing took {elapsed_time:.2f} seconds")

    # ----------------------------------------------------------------
