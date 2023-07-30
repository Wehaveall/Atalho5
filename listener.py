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
    def __init__(self):
        self.accent = False
        self.last_key = None
        self.typed_keys = ""
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

    stop_listener = Event()

    def on_key_release(self, key):
        if key in self.omitted_keys:
            if key == keyboard.Key.space:
                # Replace comma with dot for number conversion
                typed_keys_for_conversion = self.typed_keys.replace(",", ".")

                # Check if the typed keys end with "e" and its preceding characters form a number
                # Check if the typed keys end with "e" and its preceding characters form a number
                number_type = number_utils.is_number(typed_keys_for_conversion[:-1])
                if self.typed_keys.endswith("e") and number_type:
                    # Convert the number to words
                    number_in_words = number_utils.number_to_words(
                        typed_keys_for_conversion
                    )

                    # Replace the number with its word representation
                    pyautogui.hotkey("ctrl", "shift", "left")
                    pyautogui.press("backspace")
                    pyperclip.copy(number_in_words)
                    pyautogui.hotkey("ctrl", "v")

                    self.typed_keys = ""

                # Check if the typed keys end with "m" and its preceding characters form a number
                elif self.typed_keys.endswith("m") and number_utils.is_number(
                    typed_keys_for_conversion[:-1]
                ):
                    # Convert the number to currency
                    number_as_currency = number_utils.number_to_currency(
                        typed_keys_for_conversion
                    )

                    # Replace the number with its currency representation
                    pyautogui.hotkey("ctrl", "shift", "left")
                    pyautogui.press("backspace")
                    pyperclip.copy(number_as_currency)
                    pyautogui.hotkey("ctrl", "v")

                    self.typed_keys = ""

                else:
                    expansion = lookup_word_in_all_databases(self.typed_keys)
                    if expansion is not None:
                        # Save the current clipboard content
                        original_clipboard_content = pyperclip.paste()

                        # Simulate pressing ctrl+shift+left to select the last word
                        pyautogui.hotkey("ctrl", "shift", "left")
                        # Simulate pressing backspace to delete the selected text
                        pyautogui.press("backspace")
                        # Copy the expansion to clipboard
                        pyperclip.copy(format_article(expansion))
                        # Paste the expansion
                        pyautogui.hotkey("ctrl", "v")

                        # Restore the original clipboard content
                        pyperclip.copy(original_clipboard_content)

                        self.typed_keys = ""

            self.typed_keys = ""
            return
        if self.stop_listener.is_set():
            return False  # Returning False stops the pynput listener

        key_char = key.char if hasattr(key, "char") else str(key)

        if self.accent:
            self.handle_accent_key(key_char)
        elif key_char in self.accents:
            self.accent = True
            self.last_key = key_char
        else:
            self.typed_keys += key_char

            # ----------------------------------------------------------------

    def handle_accent_key(self, key_char):
        self.accent = False
        combination = self.last_key + key_char
        self.typed_keys += self.accent_mapping[combination]


def start_listener():
    listener = KeyListener()
    pynput_listener = keyboard.Listener(on_release=listener.on_key_release)
    pynput_listener.start()
    return listener, pynput_listener


def stop_keyboard_listener(listener, pynput_listener):
    listener.stop_listener.set()
    pynput_listener.join()
