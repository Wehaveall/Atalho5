from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
import time
import json

# Módulo tkinter para caixa de diálogo
from tkinter import Tk
from tkinter.filedialog import askopenfilename


class Executor:
    def __init__(self):
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    def get_macro_filename(self):
        # Primeiro, criamos uma instância de Tk e a escondemos,
        # já que não queremos uma janela completa do Tkinter.
        Tk().withdraw()

        # Mostramos a caixa de diálogo de arquivos e obtemos o caminho do arquivo selecionado.
        return askopenfilename()

    def start_macro(self, filename):
        if filename:
            self.execute_macro(filename)
        else:
            print("No file selected.")

    def execute_macro(self, filename):
        # Load the macro
        with open(filename, "r") as f:
            events = json.load(f)

        # Iterate through the events
        for event in events:
            # Extract the event type, value, and elapsed time
            event_type, value, elapsed_time = event

            # If this is a 'key' event, press the key
            if event_type == "key":
                self.keyboard.type(value)

            # If this is a 'click' event, move the mouse to the coordinates and click
            elif event_type == "click":
                x, y = value
                self.mouse.position = (x, y)
                self.mouse.click(Button.left)

            # Wait for the elapsed time before moving to the next event
            time.sleep(elapsed_time)


# Usage:
executor = Executor()
# executor.start_macro()  # Chame este método quando o usuário clicar no botão de execução da macro
