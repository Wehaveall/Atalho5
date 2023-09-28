
import win32com.client
import win32gui
import customtkinter as ctk
import time
import keyboard
import win32api  # <-- New import for getting the caret position
import ctypes
from ctypes import wintypes
import threading





class CustomTkinterPopupSelector:
    
    
    def __init__(self, options,  key_listener, event):
        
        

        # Wait for a small period to ensure the keyboard listener has fully stopped
        time.sleep(0.1)
        self.key_listener = key_listener  # Store the key_listener instance



        self.event = event


       
    
        
        self.key_listener.active = False  # Deactivate the key listener
       

        self.root = ctk.CTk()  # Using customtkinter's CTk instead of tk.Tk

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")


        self.root.withdraw()  # Hide the main window

        self.top_window = ctk.CTkToplevel(self.root)  # Using customtkinter's CTkToplevel
        
        
        # Make the window always on top
        self.top_window.wm_attributes("-topmost", 1)  # <-- New line
         # Bind the 'on_closing' method to the window close event
        self.top_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Make the window modal
        self.top_window.grab_set()
        
       # Get caret position using custom function
        x, y = self.get_caret_position()
        offset_x = 20  # Offset to move the window to the right of the caret
        offset_y = 20  # Offset to move the window below the caret
        
        
        if x is not None and y is not None:
            self.top_window.geometry(f"800x500+{x + offset_x}+{y + offset_y}")  # Adjusted to add offsets
        
        
        
        
        self.top_window.title("Select Expansion")

       
        # To capture keypress events and paste the corresponding expansion
        self.top_window.bind('<Key>', lambda event: self.on_key(event, options))
        
        
        button_width = 750  # Fixed width in pixels
        button_height = 40  # Fixed height in pixels

        for i, option in enumerate(options):
            truncated_option = option if len(option) <= 90 else option[:87] + "..."
            
            button = ctk.CTkButton(
                self.top_window,
                anchor= "w",
                text=f"{i + 1}. {truncated_option}",
                command=lambda i=i: self.make_selection(i),
                fg_color="orange",  # Set background to orange
                text_color="black",  # Set text to black
                font=ctk.CTkFont(family='Work Sans', size=16),
                width=button_width,  # Set fixed width
                height=button_height  # Set fixed height
            )
            button.place(x=10, y=10 + i * (button_height + 10))  # Set position

       
        # Attempt to bring Tkinter window to the foreground
        self.bring_window_to_foreground()


        self.root.mainloop()




######################################################################################
    def bring_window_to_foreground(self):
        self.top_window.update_idletasks()
        hwnd = win32gui.FindWindow(None, "Select Expansion")
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")
        time.sleep(0.1)
        shell.SendKeys("%")
        win32gui.SetForegroundWindow(hwnd)
        # Send another Alt key to nullify the activation
        self.top_window.focus_force()

  
  
  ####################################################################################
    def make_selection(self, index):
        

        # Explicitly reset last_sequence and typed_keys to avoid capturing keys during popup
        self.key_listener.last_sequence = ""
        self.key_listener.typed_keys = ""

        #self.callback(index)
        self.top_window.grab_release()  # Release the grab (modal state)
        self.top_window.destroy()
        self.root.quit()
         # Add a small delay here
        time.sleep(0.1)  # You can adjust the duration


        # Explicitly call paste_expansion here to test
        selected_expansion_data = self.key_listener.expansions_list[index]
        self.key_listener.paste_expansion(
            selected_expansion_data["expansion"],
            format_value=selected_expansion_data["format_value"],
        )

        time.sleep(0.1)  # Add a slight delay
        #self.key_listener.popup_open = False  # Reset the flag when popup is closed

        self.event.set()  # Notify that the popup is done


    def on_key(self, event, options):
        try:
            time.sleep(0.1)  # Add a slight delay
            index = int(event.char) - 1  # Convert to integer and 0-based index
            if 0 <= index < len(options):
                self.make_selection(index)
                self.key_listener.popup_open = True  # Use self.key_listener to access the instance variable
                return
        except ValueError:
            pass  # Ignore non-integer keypress


    def get_caret_position(self):
        class GUITHREADINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_ulong),
                        ("flags", ctypes.c_ulong),
                        ("hwndActive", ctypes.wintypes.HWND),
                        ("hwndFocus", ctypes.wintypes.HWND),
                        ("hwndCapture", ctypes.wintypes.HWND),
                        ("hwndMenuOwner", ctypes.wintypes.HWND),
                        ("hwndMoveSize", ctypes.wintypes.HWND),
                        ("hwndCaret", ctypes.wintypes.HWND),
                        ("rcCaret", ctypes.wintypes.RECT)]

        guiThreadInfo = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
    
        hwnd = win32gui.GetForegroundWindow()
    
        processID = ctypes.c_ulong()
        threadID = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(processID))  # <-- Corrected line
    
        if ctypes.windll.user32.GetGUIThreadInfo(threadID, ctypes.byref(guiThreadInfo)):
            caret_x = guiThreadInfo.rcCaret.left
            caret_y = guiThreadInfo.rcCaret.top
            return caret_x, caret_y
        else:
            return None, None
        

    def on_closing(self):
        # This method will be called when the Tkinter window is closed
        print("Window is being closed")
        self.key_listener.start_listener()  # Restart the keyboard listener
        self.event.set()  # Notify that the popup is done
        self.top_window.destroy()
        self.root.quit()