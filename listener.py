from pynput import keyboard
from collections import defaultdict
from threading import Event
import pyautogui
from src.database.data_connect import lookup_word_in_all_databases
import pyperclip  # We add this import for clipboard manipulation
from src.utils import number_utils
import time


def format_article(article):
    delimiters = ["*", "#", "%", "@", "$"]
    for delimiter in delimiters:
        article = article.replace(delimiter, "\n")
    return article


class KeyListener:
    def __init__(self, api):
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

    def on_key_release(self, key):
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
                return

            if key == keyboard.Key.space:
                typed_keys_for_conversion = self.typed_keys.replace(",", ".")

                number_type = number_utils.is_number(typed_keys_for_conversion[:-1])
                if self.typed_keys.endswith("e") and number_type:
                    number_in_words = number_utils.number_to_words(
                        typed_keys_for_conversion
                    )

                    self.pynput_listener.stop()  # Stop the listener
                    pyautogui.hotkey("ctrl", "shift", "left")
                    pyautogui.press("backspace")
                    pyperclip.copy(number_in_words)
                    pyautogui.hotkey("ctrl", "v")
                    self.start_listener()  # Start a new listener

                    self.typed_keys = ""

                elif self.typed_keys.endswith("m") and number_utils.is_number(
                    typed_keys_for_conversion[:-1]
                ):
                    number_as_currency = number_utils.number_to_currency(
                        typed_keys_for_conversion
                    )

                    self.pynput_listener.stop()  # Stop the listener
                    pyautogui.hotkey("ctrl", "shift", "left")
                    pyautogui.press("backspace")
                    pyperclip.copy(number_as_currency)
                    pyautogui.hotkey("ctrl", "v")
                    self.start_listener()  # Start a new listener

                    self.typed_keys = ""

                else:
                    expansion = lookup_word_in_all_databases(self.typed_keys)
                    if expansion is not None:
                        original_clipboard_content = pyperclip.paste()

                        self.pynput_listener.stop()  # Stop the listener
                        pyautogui.hotkey("ctrl", "shift", "left")
                        pyautogui.press("backspace")
                        pyperclip.copy(format_article(expansion))
                        pyautogui.hotkey("ctrl", "v")
                        self.start_listener()  # Start a new listener

                        pyperclip.copy(original_clipboard_content)

                        self.typed_keys = ""
                    else:
                        # If no expansion was found, clear the typed keys
                        self.typed_keys = ""

            return

        if self.stop_event.is_set():
            return False

        key_char = key.char if hasattr(key, "char") else str(key)

        if self.accent:
            self.handle_accent_key(key_char)
        elif key_char in self.accents:
            self.accent = True
            self.last_key = key_char
        else:
            self.typed_keys += key_char

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
