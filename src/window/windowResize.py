from ctypes import windll, Structure, c_long, byref
import time


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


### Get mouse X Y
def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return {"x": pt.x, "y": pt.y}


### calc window pos , size , mouse pos, mouse movement
def doresize(window):
    state_left = windll.user32.GetKeyState(
        0x01
    )  # Left button down = 0 or 1. Button up = -127 or -128
    winWbefore = window.width
    winHbefore = window.height

    mouseactive = queryMousePosition()
    beforex = mouseactive["x"]
    beforey = mouseactive["y"]

    while True:
        a = windll.user32.GetKeyState(0x01)
        if a != state_left:  # Button state changed
            state_left = a
            print(a)
            if a < 0:
                print("Left Button Pressed")
                break
            else:
                print("Left Button Released")
                break

        mouseactive = queryMousePosition()
        afterx = mouseactive["x"]
        aftery = mouseactive["y"]
        try:
            totalx = int(beforex) - int(afterx)
            totaly = int(beforey) - int(aftery)
        except:
            print("fail")
        if totalx > 0:
            changerx = winWbefore + (totalx * -1)
        else:
            changerx = winWbefore + (totalx * -1)
        if totaly > 0:
            changerY = winHbefore + (totaly * -1)
        else:
            changerY = winHbefore + (totaly * -1)

        window.resize(changerx, changerY)
        time.sleep(0.01)
