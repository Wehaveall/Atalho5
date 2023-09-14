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








def move_cursor_to_last_word(self):
        # Move cursor to the start of the last word without going to the end of the line
        pyautogui.hotkey('ctrl', 'left')





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

    
       

    # ----------------------------------------------------------------

    def paste_expansion(self, expansion, format_value):
        self.pynput_listener.stop()  # Stop listening for keys

        # Debug statements
        print(f"Debug: Expansion before copy: {expansion}")

        # Clear previously typed keys
        pyautogui.hotkey("ctrl", "shiftleft", "shiftright", "left")
        pyautogui.press("backspace")

        if expansion is not None:
            print("Actual value of format_value before casting: ", format_value)
            format_value = int(format_value)
            print("Actual value of format_value after casting: ", format_value)

            if format_value == 0:
                pyperclip.copy(expansion)
                print("Debug: Using REGULAR clipboard.")
            else:
                dirty_HTML = expansion  # Your variable
                html_clipboard.PutHtml(dirty_HTML)  # Your logic
                print("Debug: Using HTML clipboard.")

            # Now paste
            print("Debug: About to paste.")
            pyautogui.hotkey("ctrl", "v")
            print("Debug: Pasted.")

        self.typed_keys = ""
        self.just_expanded_with = None
        self.start_listener()  # Start listening for keys again

    # ----------------------------------------------------------------

    def on_key_release(self, key):
        # Initialize variables to None at the start of the function
        expansion = None
        format_value = None
        self.requires_delimiter = None
        self.delimiters = None
        key_char = None  # Initialize key_char

         # Initialize a new instance variable in __init__ to None
       

    #     # -----------------------------------------if platform.system() == 'Windows':
    #     import win32gui

    #     # MS WORD SPECIFIC
    #     # --------------------------------------- Get the title of the current window
    #     hwnd = win32gui.GetForegroundWindow()
    #     window_title = win32gui.GetWindowText(hwnd)
    #     # ----------------------------------------------------------------

    #     # Verificar se estamos no MS-WORD
    #     # Check if we're in MS Word

    #    # Check platform first
    #     if platform.system() == "Windows":
    #         # Check if we're in MS Word
    #         if "Word" in window_title:
    #             last_word = get_last_word_in_MS_Word()
    #             print(f"Last word in the document: {last_word}")
    #         # You can put other conditions here for different software if needed
    #     elif platform.system() == "Darwin":  # macOS
    #         print("This function is not supported on macOS")
    #     else:
    #         print("Unsupported OS")

            
        # -------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------


 # Initialize key_char to None at the start of the function

    


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
        if key == keyboard.Key.enter and not self.typed_keys:
            return

       
       
        if hasattr(key, 'char') and key.char:
            key_char = key.char
            
            # Check if it's an accent key
            if key_char in self.accents:
                self.accent = key_char  # Remember the last accent key
                # Don't update self.typed_keys yet, wait for next key
            
            # If the last key was an accent key, handle it
            elif self.accent:
                 combination = self.accent + key_char
                 accented_char = self.accent_mapping.get(combination, "")
                 if accented_char:  
                        self.typed_keys += accented_char  
                        print(f"Debug: Added accented character {accented_char} to typed_keys")
                 self.accent = None  # Reset the last accent key

            # If it's neither, simply append to self.typed_keys
            else:
                self.typed_keys += key_char
        
        
        
       
       
       
       
       
       
       
       
       
       
        # Initialize just_expanded to False at the beginning of the function
        just_expanded = False

        start_time = time.time()
        print(f"Self Typed Keys:----------- {self.typed_keys}")  
    

        try:
            # Check silent mode is enabled
            if self.isRecordingMacro:
                return

            if self.silent_mode:
                return

            if key in self.omitted_keys:
                if self.api.is_recording:
                    return
                


                #Inicia KeyChar
                key_char = key.char if hasattr(key, 'char') and key.char else ""




                # Handle backspace
                if key == keyboard.Key.backspace:
                    self.typed_keys = self.typed_keys[:-1]  # Remove the last character
                
                # Handle space key
                elif key == keyboard.Key.space:
                    self.typed_keys += " "
                    # Extract the last word
                    last_word = self.typed_keys.split()[-1] if self.typed_keys.split() else ''
                    print(f"Last Word:----------- {last_word}")
              
                
                # After any other char key is pressed, update self.typed_keys
                elif hasattr(key, 'char') and key.char:
                    self.typed_keys += key.char
                
                
                            
               
               
               
             




                
                try:
              
                    print("Before lookup")

                    try:
                        (
                            expansion,
                            format_value,
                            self.requires_delimiter,
                            self.delimiters,
                        ) = lookup_word_in_all_databases(self.typed_keys)

                    except (
                        ValueError
                    ):  # Handle the case where not enough values are returned
                        print("Not enough values returned from lookup")
                        expansion = (
                            format_value
                        ) = self.requires_delimiter = self.delimiters = None

                    print("After lookup")
                    print(f"Format Value: {format_value}")

                except Exception as e:
                    print(f"An exception occurred: {e}")

                print(
                    f"Requires delimiter: {self.requires_delimiter}"
                )  # Debug moved here
                print(f"Delimiters: {self.delimiters}")  # Debug moved here

                if self.delimiters is not None:
                    delimiter_list = [
                        item.strip() for item in self.delimiters.split(",")
                    ]
                else:
                    delimiter_list = []

                print(f"Delimiter list: {delimiter_list}")  # Debug

                # Add a debug line here to print the value of str(key)
                print(f"String representation of key: {str(key)}")

                key_str = self.key_to_str_map.get(str(key), str(key))
                print(f"Human-readable key: {key_str}")  # Debug

                if self.requires_delimiter == "yes":
                    if key_str in delimiter_list:  # Use the mapped string
                        print(
                            f"Attempting to paste expansion: {expansion}"
                        )  # Debug line
                        print("Delimiter matched")  # Debug

                        if expansion is not None:
                            self.just_expanded_with = key_str  # Set the flag here
                            self.paste_expansion(
                                expansion, format_value=format_value
                            )  # Use the variable format_value
                            self.typed_keys = ""  # Reset typed keys
                            just_expanded = (
                                True  # Set this to True when an expansion happens
                            )
                            print(
                                f"self.typed_keys cleared: {self.typed_keys}"
                            )  # Debug

                        else:
                            return

                elif self.requires_delimiter == "no":
                    if expansion is not None:
                        self.paste_expansion(expansion)
                        self.typed_keys = ""  # Reset typed keys
                        just_expanded = (
                            True  # Set this to True when an expansion happens
                        )
                    else:
                        self.typed_keys = (
                            ""  # Reset typed keys if no expansion is found
                        )

            if self.stop_event.is_set():
                return False

            

            # Handle word and char buffering
            
         
        
        
            
        except Exception as e:
            logging.error(f"Error in on_key_release: {e}")
            self.restart_listener()

        # Reset self.typed_keys if Enter or Space is pressed
        #resetting_keys_conditionally = [keyboard.Key.space, keyboard.Key.enter]
        #if key in resetting_keys_conditionally:
         #   self.typed_keys = ""
          #  self.char_buffer = ""  # Clear the char buffer

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
