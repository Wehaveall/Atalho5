import ctypes
import win32gui
import win32api
import win32con
import platform

class TextExtractor:
    def __init__(self):
        self.edit_hwnd = None

    def get_cursor_position(self, edit_hwnd):
        start = win32api.SendMessage(edit_hwnd, win32con.EM_GETSEL, 0, 0) & 0xFFFF
        end = (win32api.SendMessage(edit_hwnd, win32con.EM_GETSEL, 0, 0) & 0xFFFF0000) >> 16
        return start, end

    def enum_child_windows(self, hwnd, lparam):
        class_name = win32gui.GetClassName(hwnd)
        known_classes = [
            'Edit', 'RichEdit', 'RichEdit20A', 'RichEdit20W', 'RichEdit50W', 
            'TEdit', 'TMemo', 'wxWindowClassNR', 'Scintilla', 'ConsoleWindowClass', 
            'NetUIHWND', 'RICHEDIT', 'RichEditD2DPT', 'TextBox', 'View32', 
            'AfxWnd', '_WwG', 'EXCEL7'
          
        ]
        
        if class_name in known_classes:
            self.edit_hwnd = hwnd
            return False

   

    def get_text_from_foreground_window(self):
        self.edit_hwnd = None
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            print("Debug: No active window.")
            return None

        print(f"Debug: Found window with handle: {hwnd}")

        win32gui.EnumChildWindows(hwnd, self.enum_child_windows, None)
        
        if self.edit_hwnd is None:
            print("Debug: No matching class name for text area.")
            return None

        print(f"Debug: Using text area with handle: {self.edit_hwnd}")

        length = win32gui.SendMessage(self.edit_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)

        if length == 0:
            print("Debug: Text area is empty.")
            return None

        buffer = ctypes.create_unicode_buffer(length + 1)
        win32gui.SendMessage(self.edit_hwnd, win32con.WM_GETTEXT, length + 1, buffer)

        try:
            text = buffer.value
        except UnicodeDecodeError:
            print("Debug: Unicode decode error.")
            return None

        return text

    def get_word_behind_cursor(self, cursor_position, text):
        words = text[:cursor_position].split()
        if words:
            return words[-1]
        return None
