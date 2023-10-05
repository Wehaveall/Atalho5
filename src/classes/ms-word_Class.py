   
import platform

def get_last_word_in_MS_Word():
    if platform.system() == "Windows":
        import win32com.client

        word = win32com.client.Dispatch("Word.Application")
        doc = word.ActiveDocument
        content = doc.Content.Text
        words = content.split()
        if words:
            return words[-1]
        else:
            return None
    elif platform.system() == "Darwin":  # macOS
        # Code for Mac
        print("This function is not supported on macOS")
        return None
    else:
        print("Unsupported OS")
        return None