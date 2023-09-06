from pynput import keyboard
from collections import defaultdict
from threading import Event
import pyautogui
from src.database.data_connect import lookup_word_in_all_databases
import pyperclip  # We add this import for clipboard manipulation
from src.utils import number_utils
import time
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def format_article(article):
    delimiters = ["*", "#", "%", "@", "$"]
    for delimiter in delimiters:
        article = article.replace(delimiter, "\n")
    return article


class KeyListener:
    def __init__(self, api):
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
        self.api = api  # Armazene api para uso posterior
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




#----------------------------------------------------------------



    def paste_expansion(self, expansion):
        self.pynput_listener.stop()

        # Salvar conteúdo original do clipboard
        original_clipboard_content = pyperclip.paste()

        # Inserir um backspace press se a última tecla foi "Enter"
        if self.just_expanded_with == 'enter':
            pyautogui.press("backspace")

        pyautogui.hotkey("ctrl", "shiftleft", "shiftright", "left")
        pyautogui.press("backspace")

        if expansion is not None:
            logging.info("About to copy to clipboard.")
            pyperclip.copy(format_article(expansion))
            logging.info("Copied to clipboard.")

            # Verificar se o clipboard foi atualizado
            for _ in range(10):
                if pyperclip.paste() == format_article(expansion):
                    break
                time.sleep(0.1)

            logging.info("About to paste.")
            pyautogui.hotkey("ctrl", "v")
            logging.info("Pasted.")

            # Restaurar conteúdo original do clipboard
            pyperclip.copy(original_clipboard_content)

        self.typed_keys = ""
        self.just_expanded_with = None  # Resetar a flag
        self.start_listener()

#----------------------------------------------------------------


    def on_key_release(self, key):

        # Ignora enter quando não há  nada em self_typed_keys
        if key == keyboard.Key.enter and not self.typed_keys:
            return
       
        # Initialize just_expanded to False at the beginning of the function
        just_expanded = False

        start_time = time.time()

        try:
            # Check silent mode is enabled
            if self.isRecordingMacro:
                return

            if self.silent_mode:
                return

            if key in self.omitted_keys:
                if self.api.is_recording:
                    return

                if key == keyboard.Key.backspace:
                    self.typed_keys = self.typed_keys[:-1]
                    print(
                        f"Current typed_keys (After backspace): {self.typed_keys}"
                    )  # Debug
                    return

                (
                    expansion,
                    self.requires_delimiter,
                    self.delimiters,
                ) = lookup_word_in_all_databases(self.typed_keys)

                print(
                    f"Requires delimiter: {self.requires_delimiter}"
                )  # Debug moved here
                print(f"Delimiters: {self.delimiters}")  # Debug moved here

                # Convert the delimiters string to a list
                delimiter_list = [item.strip() for item in self.delimiters.split(",")]

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
                            self.paste_expansion(expansion)
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

            key_char = key.char if hasattr(key, "char") else str(key)

            # ----------------------------------------------------------------
            if not just_expanded:
                if self.accent:
                    self.handle_accent_key(key_char)
                elif key_char in self.accents:
                    self.accent = True
                    self.last_key = key_char
                else:
                     if key not in self.omitted_keys:
                        self.typed_keys += key_char
                        print(self.typed_keys)
                                

            just_expanded = False

        # --------------------------------------------------------

        except Exception as e:
            logging.error(f"Error in on_key_release: {e}")
            self.restart_listener()  # Restart the listener in case of an error

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
        self.typed_keys += self.accent_mapping[combination]

    def start(self):
        self.start_listener()  # Change self.listener.start() to self.start_listener()

    def stop(self):
        self.stop_listener()  # Change self.listener.stop() to self.stop_listener()


def stop_keyboard_listener(listener):
    listener.stop_listener()  # Remove the second argument, pynput_listener
