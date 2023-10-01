import ctypes

# Define POINT structure
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# Load necessary DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_caret_position():
    """Get the screen coordinates of the caret in the currently active window."""

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

