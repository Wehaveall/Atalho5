import ctypes
from queue import Empty
import tkinter as tk
from tkinter import Button
from functools import partial
import pyautogui
import pygetwindow as gw

# Load necessary DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


# All your existing methods can be here, like `get_caret_position`, `truncate_text`, etc.


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


def create_popup(
    tk_queue, key_listener_instance, stop_threads
):  # Added stop_threads as an argument
    print("Entered create_popup")
    root = None
    should_create_popup = False  # Add this flag

    def destroy_popup():
        print("destroy_popup called")  # Debug print
        nonlocal root, should_create_popup  # Add should_create_popup here
        print(f"Root is None: {root is None}")  # Debug print

        if root is not None:
            print("Received message: destroy_popup")
            root.destroy()
            # Restart the keyboard listener here
            should_create_popup = False  # Reset the flag when destroying the popup

            try:
                key_listener_instance.start_listener()  # Assuming `start_listener` is the method to restart the listener
                print("Listener restarted successfully")
            except Exception as e:
                print(f"Failed to restart the listener: {e}")

    def create_popup_internal():
        nonlocal root, should_create_popup  # Add should_create_popup here
        print("About to stop listener and create popup")
        key_listener_instance.stop_listener()

        root = tk.Tk()
        root.title("Select Expansion")
        # Register the destroy_popup function for the close button
        root.protocol("WM_DELETE_WINDOW", destroy_popup)  # Add this line

        caret_x, caret_y = get_caret_position()

        print(f"Caret position: x={caret_x}, y={caret_y}")

        # Set the window size and position it below the caret
        window_width = 500
        window_height = 300
        root.geometry(f"{window_width}x{window_height}+{caret_x}+{caret_y}")

        root.attributes("-topmost", True)  # This line makes the window stay on top
        # root.grab_set()  # This line captures all events
        # Make sure the window is created
        root.update_idletasks()
        root.update()

        for i, option in enumerate(key_listener_instance.expansions_list):
            raw_button_text = (
                option["expansion"] if "expansion" in option else "Undefined"
            )
            button_text = truncate_text(raw_button_text, 60)
            button = Button(
                root,
                text=button_text,
                command=partial(key_listener_instance.make_selection, i, root),
                font=("Work Sans", 11),
                anchor="w",
            )
            button.pack(fill=tk.X, padx=10, pady=5)
        should_create_popup = True  # Set the flag to True when the popup is created

        ## Simulate the mouse click to focus the popup window
        windows = gw.getWindowsWithTitle("Select Expansion")
        if windows:
            popup_win = windows[0]
            pyautogui.click(popup_win.left + 10, popup_win.top + 10)

    while not stop_threads.is_set():  # Using the passed-in stop_threads
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

        if should_create_popup:  # Check the flag before running the main loop
            root.mainloop()
            should_create_popup = (
                False  # Reset the flag after the main loop is terminated
            )

    print("Popup thread stopped")
