from utils.gui import create_gui
from utils.hp_mp_functions import check_hp_mp
from pynput import keyboard


# ESC and F11 key listener
def on_press(key):
    try:
        if key == keyboard.Key.esc:
            stop_auto_attack()
            stop_hp_mp_check()
        elif key == keyboard.Key.f11:
            start_auto_attack()
            start_hp_mp_check()
    except AttributeError:
        pass


# Start the key listener
def start_global_key_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()


if __name__ == "__main__":
    start_global_key_listener()
    create_gui()