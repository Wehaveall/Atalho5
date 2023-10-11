# Standard Libraries
from collections import defaultdict, deque
from functools import partial
from threading import Event
import json
import logging
import platform
import re
import time

# Third-Party Libraries
import html_clipboard
import keyboard  # Replacing pynput
import pyautogui
import pyperclip  # Added for clipboard manipulation

# Project-Specific Libraries
from src.database.data_connect import lookup_word_in_all_databases
from src.utils import number_utils
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
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")





global cursor_row  # Declare cursor_row as global to modify it
global cursor_col  # Declare cursor_col as global to modify it

cursor_row = 0
cursor_col = 0


######################################################    KEYLISTENER    ###############################################################
########################################################################################################################################
class KeyListener:
    
    
    def __init__(self, api, tk_queue=None):  # Add tk_queue as an optional parameter
       
        self.just_suffix = False
        self.tk_queue = tk_queue  # Assign it to an instance variable
        # self.popup_done_event = threading.Event()
        self.expansions_list = []  # Define the expansions_list
        # keyboard.add_abbreviation("@g", "denisvaljean@gmail.com")
        self.programmatically_typing = False  # Initialize the flag here
        self.last_word = ""  # Initialize last_word
        self.word_buffer = deque([], maxlen=500)  # Initialize with an empty deque
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
        self.cursor_row = 0
        self.cursor_col = 0
        self.multi_line_string = """"""
        self.typed_keys = """"""
        self.lines = """"""

        # Added this line to store the pynput listener
        # self.pynput_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)

        self.accent_mapping = defaultdict(lambda: "", {"~a": "ã", "~A": "Ã", "~o": "õ", "~O": "Õ", "~n": "ñ", "~N": "Ñ", "´a": "á", "´A": "Á", 
        "´e": "é", "´E": "É", "´i": "í", "´I": "Í", "´o": "ó", "´O": "Ó", "´u": "ú", "´U": "Ú", "`a": "à", "`A": "À", "`e": "è", "`E": "È",
        "`i": "ì", "`I": "Ì", "`o": "ò", "`O": "Ò", "`u": "ù", "`U": "Ù", "^a": "â", "^A": "Â", "^e": "ê", "^E": "Ê", "^i": "î", "^I": "Î",
        "^o": "ô", "^O": "Ô", "^u": "û", "^U": "Û"})
        
        
        self.accents = set(["~", "´", "`", "^"])
        
        
        self.omitted_keys = set(["esc", "shift", "ctrl", "alt", "cmd", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        "page up", "page down", "home", "end", "delete", "insert", "up", "down", "left", "right", "backspace", "print screen", "scroll lock", "pause",
        "space", "caps lock", "tab", "enter", "num lock", "right ctrl", "left ctrl", "left shift", "right shift"])

        self.resetting_keys = set(["space"])

    
    ###################################################################### FUNCTIONS
    #TO DO - newline must be configurable in the GUI
    
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
                    art_split = section.split("Art.", 1)  # Split by the first occurrence of "Art."
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
                new_article = new_article[:first_art_index] + "\n" * newlines + new_article[first_art_index:]

        return new_article

    
    def stop_listener(self):
        print("Stopping Listener from Listerner.py")
        try:
            keyboard.unhook(self.press_hook)
            keyboard.unhook(self.release_hook)
            print("Successfully unhooked the keyboard listeners.")
        except Exception as e:
            print(f"An error occurred while unhooking: {e}")

    def start_listener(self):
        print("Starting Listener from Listerner.py")
        try:
            self.press_hook = keyboard.on_press(lambda e: self.on_key_press(e))
            self.release_hook = keyboard.on_release(lambda e: self.on_key_release(e))
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
                self.typed_keys = (
                    self.typed_keys[: -len(last_word) - 1] + converted_word + " "
                )

            elif self.typed_keys.endswith(last_word):
                self.typed_keys = (
                    self.typed_keys[: -len(last_word)] + converted_word + " "
                )

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
          # Debug: Print before changes
        print(f"Before paste: Multi-line string: {self.multi_line_string}, Cursor col: {self.cursor_col}")


        # Clear previously typed keys
        keyboard.press("ctrl")
        keyboard.press("shift")
        keyboard.press_and_release("left arrow")
        keyboard.release("shift")
        keyboard.release("ctrl")
        keyboard.press_and_release("backspace")

        if expansion is not None:
            # Format the expansion before pasting (This is the new line)
            formatted_expansion = self.format_article(expansion, newlines=2) 
            
            format_value = int(format_value)

            if format_value == 0:
                pyperclip.copy(formatted_expansion)  # Modified to use formatted_expansion
                print("Debug: Using REGULAR clipboard.")
            else:
                dirty_HTML = formatted_expansion  # Modified to use formatted_expansion
                html_clipboard.PutHtml(dirty_HTML)  # Your logic
                print("Debug: Using HTML clipboard.")

            # Now paste
            keyboard.press_and_release("ctrl+v")

            # Move the mouse 1 pixel to the right (This is the new line)
            # Provisional solution because paste will only appear after mouse move
            current_x, current_y = pyautogui.position()  # Get current mouse position
            pyautogui.moveTo(current_x + 1, current_y)  # Move mouse 1 pixel to the right


        self.programmatically_typing = False  # Reset the flag

        # Remove the last incorrect word from self.typed_keys
        self.typed_keys = self.typed_keys.rstrip(self.last_word)

        # Add the corrected word
        self.typed_keys += formatted_expansion   # Modified to use formatted_expansion

        self.last_word = formatted_expansion  # Modified to use formatted_expansion
        self.word_buffer.append(formatted_expansion)  # Modified to use formatted_expansion
        print(f"After paste: Multi-line string: {self.multi_line_string}, Cursor col: {self.cursor_col}")
 
 
       





    # ----------------------------------------------------------------Handle Accents

    def handle_accents(self, key_char):
        if key_char in self.accents:
            self.accent = key_char
            return None  # No character to append to multi_line_string

        elif self.accent:
            combination = self.accent + key_char
            accented_char = self.accent_mapping.get(combination, "")

            if accented_char:
                self.typed_keys += accented_char
                self.last_sequence += accented_char  # Update last_sequence here
                self.accent = None
                return accented_char  # Return the accented character

            self.accent = None

        else:
            self.typed_keys += key_char
            self.last_sequence += key_char  # Update last_sequence here
            return key_char  # Return the original character

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

        # Split the multi_line_string into lines
        lines = self.multi_line_string.split("\n")

        # Get the current line
        current_line = lines[self.cursor_row]

       # Find the last occurrence of the typed shortcut in the current line-----------------LAST SEQUENCEE _ NOT LAST WORD---------------------------------------------
        last_occurrence = current_line.rfind(self.last_sequence)

        # Remove the last typed shortcut from the current line
        if last_occurrence != -1:
            current_line = current_line[:last_occurrence] + current_line[last_occurrence + len(self.last_sequence):]


        # Add the selected expansion to the current line
        new_current_line = current_line + expansion_to_paste
        lines[self.cursor_row] = new_current_line

        # Update the multi_line_string
        self.multi_line_string = "\n".join(lines)

        # Update the cursor position to the end of the new line
        self.cursor_col = len(new_current_line)

        # Reset self.typed_keys and self.last_sequence to the selected expansion
        self.typed_keys = expansion_to_paste
        self.last_sequence = expansion_to_paste

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

   
   
    # ------------------------------------------------------------------------#
   
    def handle_hardcoded_suffixes(self, last_word):
        hardcoded_suffixes = {
            "çao": ("ção", r"(?<![ã])\bçao\b"),
            "mn": ("mento", r".mn"),
            "ao": ("ão", r".ao"),
        }

        for i in range(len(last_word) - 1, -1, -1):
            suffix = last_word[i:]
            if suffix in hardcoded_suffixes:
                expansion, regex_pattern = hardcoded_suffixes[suffix]
                if re.search(regex_pattern, last_word):
                    prefix = last_word[:i]
                    expansion = prefix + expansion

                    # Remove the last typed word from the current line
                    lines = self.multi_line_string.split("\n")
                    current_line = lines[self.cursor_row]
                    lines[self.cursor_row] = current_line[:self.cursor_col - len(last_word)]
                    self.multi_line_string = "\n".join(lines)

                    return (expansion, True)  # Return expansion and flag as True
        return (None, False)  # Return None and flag as False if no match



    def lookup_and_expand(self, sequence):
        words = word_tokenize(sequence)
        last_word = words[-1] if words else ""

        
        # Suffix Function
        expansion, suffix_used = self.handle_hardcoded_suffixes(last_word)  # Get both expansion and flag
        #####################################################################
       

        if expansion:

         
            if suffix_used:
                self.just_suffix = True
                print("Expansion came from hardcoded suffixes###################################")
              

                # Remove the last word from typed_keys
                if self.typed_keys.endswith(last_word + " "):
                    self.typed_keys = self.typed_keys[:-len(last_word) - 1]
                elif self.typed_keys.endswith(last_word):
                    self.typed_keys = self.typed_keys[:-len(last_word)]

                # Paste the new expansion
                self.paste_expansion(expansion, format_value=0)

                # Update multi-line string
                lines = self.multi_line_string.split("\n")
                current_line = lines[self.cursor_row]
                new_line = current_line[:self.cursor_col - len(last_word)] + expansion + current_line[self.cursor_col:]
                lines[self.cursor_row] = new_line
                self.multi_line_string = "\n".join(lines)

                ### FALTA RECUPERAR O CONTEÚDO ANTERIOR AO SUFIXO. ERRO, CURSOR E CHARS DUPLICADOS.


                # Update last_sequence
                self.last_sequence = expansion

                # Remove the last character from multi_line_string and append the expansion
                #self.multi_line_string = expansion

                # Update cursor position to the last position of the multi_line_string
                self.cursor_col = len(self.multi_line_string)
    
                return
       
       
       
       
        # Remove the last word from typed_keys
            if self.typed_keys.endswith(last_word + " "):
                self.typed_keys = self.typed_keys[:-len(last_word) - 1]
            elif self.typed_keys.endswith(last_word):
                self.typed_keys = self.typed_keys[:-len(last_word)]

            # Update multi-line string
            lines = self.multi_line_string.split("\n")
            current_line = lines[self.cursor_row]
            new_line = current_line[:self.cursor_col - len(last_word)] + expansion + current_line[self.cursor_col:]
            lines[self.cursor_row] = new_line
            self.multi_line_string = "\n".join(lines)

            # Update cursor position
            self.cursor_col = self.cursor_col - len(last_word) + len(expansion)

            # Update last_sequence
            self.last_sequence = expansion

            # Paste the new expansion
            self.paste_expansion(expansion, format_value=0)

            # Clear the word buffer
            if self.word_buffer and self.word_buffer[-1] == last_word:
                self.word_buffer.pop()

            # Set flag to skip next key press
            self.skip_next_key_press = True

            return

        try:
            expansions_list = lookup_word_in_all_databases(sequence)
        except ValueError:
            print("Not enough values returned from lookup")

        ################################################################    MULTIPLE EXPANSIONS
        if len(expansions_list) > 1:
            self.expansions_list = expansions_list  # Store the expansions list

            self.create_popup()  # Call the create_popup function to create a Tkinter window

        

        ###############################################################     ONE EXPANSION
        elif len(expansions_list) == 1:  # Handling single expansion
            print("Debug: Single expansion detected.")  # Debugging line
            expansion_data = expansions_list[0]
            self.paste_expansion(
                expansion_data["expansion"], format_value=expansion_data["format_value"]
            )

        ######
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

        #####
        if self.requires_delimiter == "yes":
            delimiter_list = [item.strip() for item in self.delimiters.split(",")]
            key_str = self.key_to_str_map.get(str(self.last_key), str(self.last_key))
            if key_str in delimiter_list:
                if expansion is not None:
                    self.paste_expansion(expansion, format_value=format_value)
                    self.typed_keys = """"""

        elif self.requires_delimiter == "no":
            if expansion is not None:
                self.paste_expansion(expansion, format_value=format_value)
                self.typed_keys = """"""

    # ----------------------------------------------------------------

    # def on_key_press(self, event):
    #     key = event.name  # Define 'key' first before using it
    #     print(f"Key pressed: {key}")  # Debugging
    #     if key == "shift":
    #         self.shift_pressed = True

    ################################################################
    ################################################################

    def on_key_press(self, event):
        processed_char = None
        next_char = None  # Initialize next_char to None
        char = None  # Highlighted Change

      
        
        if (self.programmatically_typing):  # Skip if we are programmatically typing or popup is open
            return

        print("on_key_press called" )  # Debugging: Changed from on_key_release to on_key_press
        key = event.name
        print(f"Key pressed: {key}")  # Debugging: Changed from Key released to Key pressed

        # Initialize variables to None at the start of the function
        expansion = None
        format_value = None
        self.requires_delimiter = None
        self.delimiters = None

        start_time = time.time()

        # Initialize self.last_sequence if not already done
        if not hasattr(self, "last_sequence"):
            self.last_sequence = ""

        if (self.ctrl_pressed or self.shift_pressed or self.alt_pressed or self.winkey_pressed):
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

        # Ignore 'space' when self.typed_keys is empty
        if key == "space" and not self.typed_keys:
            return

        if key not in self.omitted_keys:
            # key = event.name
            # Update the multi-line string here
            # self.multi_line_string += key

            if self.shift_pressed:
                char = key.upper()  # Convert to upper case if Shift is pressed
                self.shift_pressed = False  # Reset the flag immediately after use

            else:
                char = key

            processed_char = self.handle_accents(char)  # Call handle_accents and save the returned character

            print(f"Self Typed Keys:__ {self.typed_keys}")
            print(f"Last Sequence:__1 {self.last_sequence}")

        else:  # Key is in omitted_keys
            if key == "backspace":
                self.typed_keys = self.typed_keys[:-1]
                self.last_sequence = self.last_sequence[:-1]  # Update last_sequence

            elif key == "space":
                self.typed_keys += " "
                self.last_sequence = ""  # Clear last_sequence
              
                

            elif key == "enter":  # Handling the "Enter" key
                # self.typed_keys += '\n' # Add newline to last_typed_keys
                self.last_sequence = ""  # Clear last_sequence


            # Highlighted Changes: Start
            elif key == "left":
                self.cursor_col = max(0, self.cursor_col - 1)

            elif key == "right":
                next_char = (
                    self.multi_line_string[self.cursor_col]
                    if self.cursor_col < len(self.multi_line_string)
                    else None
                )

                if next_char:
                    self.cursor_col = min(
                        len(self.multi_line_string), self.cursor_col + 1
                    )

            elif key == "up":
                # Removed cursor movement, only reset last_sequence
                self.last_sequence = ""

            elif key == "down":
                # Removed cursor movement, only reset last_sequence
                self.last_sequence = ""

            # ---------------------------------------WORDS--------------------------------
            # Tokenize the sentence into words
            words = word_tokenize(self.typed_keys)

            # Get the last word only if words list is not empty
            last_word = words[-1] if words else None  # Highlighted Change

            if (
                last_word
            ):  # Highlighted Change: Only call fix_double_caps if last_word is not None
                if (
                    key != "backspace"
                ):  # Highlighted Change: Add condition to skip "backspace"
                    self.fix_double_caps(last_word)  # Call fix_double_caps here
                    self.lookup_and_expand(last_word)

            # --------------------------------------SENTENCES-----------------------------
            # Sentence Tokenization
            sentences = sent_tokenize(self.typed_keys)
            last_sentence = sentences[-1] if sentences else ""
            last_sentence = sentences[-1] if sentences else None  # Highlighted Change

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

        if (
            processed_char is not None
        ):  # Update multi_line_string using the returned character
            lines = self.multi_line_string.split("\n")
            current_line = lines[self.cursor_row]
            lines[self.cursor_row] = (
                current_line[: self.cursor_col]
                + processed_char
                + current_line[self.cursor_col :]
            )
            self.cursor_col += 1  # Move the cursor to the right by 1 position
            self.multi_line_string = "\n".join(lines)

        elif key == "backspace":
            if (
                self.cursor_row < len(self.multi_line_string.split("\n"))
                and self.cursor_col > 0
            ):  # Highlighted Change: Added checks
                # Update the line at the cursor position within the specific line
                lines = self.multi_line_string.split("\n")
                current_line = lines[self.cursor_row]
                lines[self.cursor_row] = (
                    current_line[: max(0, self.cursor_col - 1)]
                    + current_line[self.cursor_col :]
                )
                self.cursor_col = max(0, self.cursor_col - 1)  # Update cursor position
                # Join the lines back into a single string
                self.multi_line_string = "\n".join(lines)

       
        elif key == "delete":
            if (
                self.cursor_row < len(self.multi_line_string.split("\n"))
                and self.cursor_col < len(self.multi_line_string.split("\n")[self.cursor_row])
            ):  # Highlighted Change: Added checks for "delete"
                # Update the line at the cursor position within the specific line
                lines = self.multi_line_string.split("\n")
                current_line = lines[self.cursor_row]
                lines[self.cursor_row] = (
                    current_line[: self.cursor_col]
                    + current_line[self.cursor_col + 1 :]
                )
                # Cursor position remains the same for "delete"
                # Join the lines back into a single string
                self.multi_line_string = "\n".join(lines)

        
        elif key == "space":
            
            # Update the line at the cursor position within the specific line
            lines = self.multi_line_string.split("\n")
            current_line = lines[self.cursor_row]
            lines[self.cursor_row] = (
                current_line[: self.cursor_col] + " " + current_line[self.cursor_col :]
            )
            self.cursor_col += 1  # Move the cursor to the right by 1 position
            # Join the lines back into a single string
            self.multi_line_string = "\n".join(lines)
            
           
             

        elif key == "enter":  # Highlighted Changes: Start
            lines = self.multi_line_string.split("\n")
            current_line = lines[self.cursor_row]
            # Split the current line at the cursor and create a new line
            lines.insert(self.cursor_row + 1, current_line[self.cursor_col :])
            lines[self.cursor_row] = current_line[: self.cursor_col]
            self.cursor_row += 1  # Move the cursor down to the new line
            self.cursor_col = 0  # Move the cursor to the beginning of the new line
            self.multi_line_string = "\n".join(lines)
            # Highlighted Changes: End

        # Update last_sequence with the last word in multi_line_string
        words_in_multi_line_string = word_tokenize(self.multi_line_string)
        if words_in_multi_line_string:
            self.last_sequence = words_in_multi_line_string[-1]  # Take the last word
        else:
            self.last_sequence = ""  # If no words, set to empty string

    

        print("Current multi-line string-------------------------------------------:")
        print(self.multi_line_string)
        print(f"Last Sequence:__2 {self.last_sequence}")

        try:
            self.last_key = key

            if key not in self.omitted_keys:
                   
                if (key != "backspace"):  # Highlighted Change: Add condition to skip "backspace" triggering shortcuts
                    self.lookup_and_expand(self.last_sequence)

            else:
                
                if key == "space":


                 
                   
                    if (key != "backspace"):  # Highlighted Change: Add condition to skip "backspace" triggering shortcuts
                        
                        self.lookup_and_expand(last_word)
                        # Tokenize the sentence into words
                        words = word_tokenize(self.multi_line_string)

                        # Get the last word

                        # Get the last word only if words list is not empty
                        last_word = words[-1] if words else None  # Highlighted Change
                        self.lookup_and_expand(last_word)

        except Exception as e:
            logging.error(f"Error in on_key_release: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"on_key_release processing took {elapsed_time:.2f} seconds")

    # ----------------------------------------------------------------
