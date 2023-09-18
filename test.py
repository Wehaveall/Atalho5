from pynput.keyboard import Listener, Key
  
# Initialize variables
shift_pressed = False
accumulated_keys = ""
  
def press_on(key):
    global shift_pressed, accumulated_keys 
 
    if key == Key.shift or key == Key.shift_r:
        shift_pressed = True
    if hasattr(key, 'char') and key.char:  # Check if the key has a printable character
        if shift_pressed:
            accumulated_keys += key.char.upper()
        else:
            accumulated_keys += key.char
 
  
def press_off(key):
    global shift_pressed
  
    if key == Key.shift or key == Key.shift_r:
        shift_pressed = False
  
    print(f"Accumulated keys: {accumulated_keys}")
  
    if key == Key.esc:
        return False
  
with Listener(on_press=press_on, on_release=press_off) as listener:
    listener.join()