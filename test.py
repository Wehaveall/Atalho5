import keyboard

def on_key_press(event):
    print(f"Key pressed: {event.name}")

def on_key_release(event):
    print(f"Key released: {event.name}")

keyboard.on_press(on_key_press)
keyboard.on_release(on_key_release)

keyboard.wait('esc')
