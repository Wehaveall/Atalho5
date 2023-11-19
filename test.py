import ctypes


def is_numlock_on():
    # GetKeyState function retrieves the status of the specified key
    # VK_NUMLOCK (0x90) is the virtual-key code for the NumLock key
    return ctypes.windll.user32.GetKeyState(0x90) != 0


# Example usage
if is_numlock_on():
    print("NumLock is ON")
else:
    print("NumLock is OFF")
