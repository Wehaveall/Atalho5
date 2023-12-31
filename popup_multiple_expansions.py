import ctypes
from queue import Empty
import tkinter as tk
from tkinter import Button
from functools import partial
import pyautogui
import pygetwindow as gw
import re

# Load necessary DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


# New function for formatting text of the buttons of the popup
def format_expansion(expansion, table_name):
    if table_name == "aTable":
        expansion = re.sub(r"[$#%&@*]", "", expansion)
        expansion = re.sub(r"\+\+", "", expansion)
    return expansion


# All your existing methods can be here, like `get_caret_position`, `truncate_text`, etc.


# Get Caret Positiom -  Work in MS Word - Wont work in NOTEPAD
def get_caret_position():
    # Get current thread ID from kernel32.dll
    current_thread_id = kernel32.GetCurrentThreadId()
    # Get the window handle for the current foreground window
    foreground_window = user32.GetForegroundWindow()
    # Get the thread ID of the process that created the window
    window_thread_id = user32.GetWindowThreadProcessId(foreground_window, None)
    # Attach the current thread to the window's thread to share input states
    user32.AttachThreadInput(current_thread_id, window_thread_id, True)
    # Initialize POINT for caret position
    caret_pos = POINT()
    # Get the caret's position
    user32.GetCaretPos(ctypes.byref(caret_pos))
    # Get the window handle that has the keyboard focus
    focused_window = user32.GetFocus()
    # Convert the caret's position to screen coordinates
    user32.ClientToScreen(focused_window, ctypes.byref(caret_pos))
    # Detach the current thread from the window's thread
    user32.AttachThreadInput(current_thread_id, window_thread_id, False)
    return (caret_pos.x, caret_pos.y)


def truncate_text(text, max_length):
    return text[: max_length - 3] + "..." if len(text) > max_length else text


def on_enter(event):
    event.widget.config(bg="#fbb347")  # Change background to light orange


def on_leave(event):
    event.widget.config(bg="SystemButtonFace")  # Change background to default


def create_popup(tk_queue, key_listener_instance, stop_threads):
    print("Entered create_popup")
    root = None
    is_popup_active = False  # New flag to track popup state

    def destroy_popup():
        nonlocal root, is_popup_active
        if root is not None:
            print("Received message: destroy_popup")
            root.destroy()
            root = None
            is_popup_active = False  # Reset the flag when popup is destroyed

            try:
                key_listener_instance.start_listener()
                print("Listener restarted successfully")
            except Exception as e:
                print(f"Failed to restart the listener: {e}")

    def create_popup_internal():
        nonlocal root, is_popup_active
        if is_popup_active:  # Check if popup is already active
            return  # Exit if popup is already active

        print("About to stop listener and create popup")
        key_listener_instance.stop_listener()

        root = tk.Tk()
        root.title("Escolha a Expansão")
        root.protocol("WM_DELETE_WINDOW", destroy_popup)

        # Bind numeric keys (1-9) to the root window
        # Moved the key_press function and root.bind here, after root is initialized
        def key_press(event):
            index = (
                int(event.char) - 1
            )  # Convert the key character to an index (0-based)
            if 0 <= index < len(key_listener_instance.expansions_list):
                key_listener_instance.make_selection(index, root)

        root.bind("<Key-1>", key_press)
        root.bind("<Key-2>", key_press)
        root.bind("<Key-3>", key_press)
        root.bind("<Key-4>", key_press)
        root.bind("<Key-5>", key_press)
        root.bind("<Key-6>", key_press)
        root.bind("<Key-7>", key_press)
        root.bind("<Key-8>", key_press)
        root.bind("<Key-9>", key_press)

        caret_x, caret_y = get_caret_position()

        window_width = 500
        window_height = 300
        root.geometry(f"{window_width}x{window_height}+{caret_x}+{caret_y}")

        root.attributes("-topmost", True)
        root.update_idletasks()
        root.update()

        # Create a frame to hold all the buttons and center it
        frame = tk.Frame(
            root,
            bg="SystemButtonFace",
        )
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for i, option in enumerate(key_listener_instance.expansions_list):
            raw_button_text = option.get("expansion", "Undefined")
            # Use the format_expansion function here
            formatted_button_text = format_expansion(raw_button_text, "aTable")
            button_text = f"{i + 1}. {truncate_text(formatted_button_text, 60)}"  # Show number followed by a dot

            button = tk.Button(
                frame,
                text=button_text,
                command=partial(key_listener_instance.make_selection, i, root),
                font=("Work Sans", 11),
                anchor="w",
            )
            button.pack(fill=tk.X, padx=10, pady=5)

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        # Create Close button and align it to bottom right
        close_button = tk.Button(
            frame, text="Fechar", command=destroy_popup, font=("Work Sans", 11)
        )
        close_button.pack(side=tk.RIGHT, padx=10, pady=5)  # <-- Align to bottom-right

        is_popup_active = True  # Set the flag when popup is created

        ## Simulate the mouse click to focus the popup window
        windows = gw.getWindowsWithTitle("Escolha a Expansão")
        if windows:
            popup_win = windows[0]
            pyautogui.click(popup_win.left + 10, popup_win.top + 10)

    while not stop_threads.is_set():
        try:
            queue_data = tk_queue.get(timeout=0.5)
            msg = queue_data[0]

            if msg == "destroy_popup":
                destroy_popup()
                continue

            if msg == "create_popup":
                create_popup_internal()

        except Empty:
            continue

        if is_popup_active:  # Check the flag before running the main loop
            root.mainloop()
            is_popup_active = False  # Reset the flag when mainloop exits

    print("Popup thread stopped")