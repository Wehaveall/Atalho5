import win32gui
import win32process
import win32api
import time


time.sleep(5)
fg_win = win32gui.GetForegroundWindow()
fg_thread, fg_process = win32process.GetWindowThreadProcessId(fg_win)
current_thread = win32api.GetCurrentThreadId()
win32process.AttachThreadInput(current_thread, fg_thread, True)
try:
    print(win32gui.GetCaretPos())
finally:
    win32process.AttachThreadInput(current_thread, fg_thread, False)  # detach
