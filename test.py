import threading
import tkinter as tk
import webview
import queue
import keyboard
import time

# Use an Event object to signal all threads to stop
stop_threads = threading.Event()


def keyboard_listener(q):
    print("Keyboard listener started")  # Debugging
    while not stop_threads.is_set():
        event = keyboard.read_event()
        if event.event_type == "down":
            q.put(("key_event", event.name))
        time.sleep(0.1)
    print("Keyboard listener stopped")  # Debugging


def on_closed():
    print("on_closed triggered")  # Debugging
    stop_threads.set()


def create_popup(tk_queue):
    print("Popup thread started")  # Debugging
    while not stop_threads.is_set():
        try:
            msg, data = tk_queue.get(timeout=1)  # Timeout after 1 second
            if stop_threads.is_set():
                break
            if msg == "key_event":
                root = tk.Tk()
                label = tk.Label(root, text=f"Key pressed: {data}")
                label.pack()
                if not stop_threads.is_set():
                    root.mainloop()
                else:
                    root.destroy()
        except queue.Empty:
            if stop_threads.is_set():
                break
            continue
    print("Popup thread stopped")  # Debugging


def start_app(tk_queue):
    # Start tkinter popup in a new thread
    popup_thread = threading.Thread(target=create_popup, args=(tk_queue,))
    popup_thread.start()

    # Start keyboard listener in a new thread
    keyboard_thread = threading.Thread(target=keyboard_listener, args=(tk_queue,))
    keyboard_thread.start()

    # Create and show pywebview window
    window = webview.create_window("Hello", "https://www.google.com")
    window.events.closed += on_closed  # Attach close event handler

    # Start pywebview in the main thread
    webview.start()

    # Stop all threads when pywebview window is closed
    popup_thread.join()
    keyboard_thread.join()


if __name__ == "__main__":
    tk_queue = queue.Queue()
    start_app(tk_queue)
