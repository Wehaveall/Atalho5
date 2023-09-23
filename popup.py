
import win32com.client
import win32gui
import win32con
import customtkinter as ctk
import time
import keyboard




class CustomTkinterPopupSelector:
    
    
    def __init__(self, options,  key_listener):
        
        
        #Stop keyboard listener
        keyboard.unhook_all()

        # Wait for a small period to ensure the keyboard listener has fully stopped
        time.sleep(0.1)
        self.key_listener = key_listener  # Store the key_listener instance
        self.key_listener.popup_open = True  # Set the flag when popup is open
        print(f"Debug: Setting popup_open to True in CustomTkinterPopupSelector")  # Debug log
        

        self.key_listener.active = False  # Deactivate the key listener
       


        self.root = ctk.CTk()  # Using customtkinter's CTk instead of tk.Tk
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")


        self.root.withdraw()  # Hide the main window

        self.top_window = ctk.CTkToplevel(self.root)  # Using customtkinter's CTkToplevel
        self.top_window.geometry("1200x500")
        self.top_window.title("Select Expansion")

        # Make the window modal
        self.top_window.grab_set()



         # To capture keypress events and paste the corresponding expansion
        self.top_window.bind('<Key>', lambda event: self.on_key(event, options))

        for i, option in enumerate(options):
            button = ctk.CTkButton(
                self.top_window,
                text=f"{i + 1}. {option}",
                command=lambda i=i: self.make_selection(i),
                fg_color="orange",  # Set background to orange
                text_color="black",    # Set text to black
                font=ctk.CTkFont(family='Work Sans', size=16),
              
            )
            button.pack(padx=10, pady=10, anchor='w')  # Left-align buttons


        # Attempt to bring Tkinter window to the foreground
        self.bring_window_to_foreground()
      
        self.root.mainloop()



######################################################################################
    def bring_window_to_foreground(self):
        self.top_window.update_idletasks()
        hwnd = win32gui.FindWindow(None, "Select Expansion")
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")
        time.sleep(0.05)
        shell.SendKeys("%")
        win32gui.SetForegroundWindow(hwnd)
        # Send another Alt key to nullify the activation
        self.top_window.focus_force()

  
  
  ####################################################################################
    def make_selection(self, index):
        
        
        print(f"Debug: make_selection called. Popup open before: {self.key_listener.popup_open}")

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

        print(f"Debug: make_selection called. Popup open after: {self.key_listener.popup_open}")
        #Restart keyboard listener
        #self.key_listener.start_listener()

        # Add a small delay here
        #time.sleep(0.1)  # You can adjust the duration


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

