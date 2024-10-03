from pynput import keyboard

import utils.shared as shared
from utils.auto_attack import start_auto_attack, stop_auto_attack
from utils.gui import create_gui
from utils.hp_mp import start_hp_mp_check, stop_hp_mp_check
from utils.loader import load_config


# ESC and F11 key listener
def on_press_events_toggle(key):
    try:
        if key == keyboard.Key.esc:  # Stop the bot
            stop_threads()
            print("Bot Stopped")
        elif key == keyboard.Key.f11:  # Start the bot
            start_threads()
            print("Bot Started")
    except AttributeError:
        pass
    except Exception as e:
        print(f"on_press_event failed: {e}")


def start_global_key_listener():
    listener = keyboard.Listener(on_press=on_press_events_toggle)
    shared.config = load_config()
    listener.start()


def stop_threads():
    if shared.auto_attack_thread:
        shared.auto_attack_thread = stop_auto_attack(shared.auto_attack_thread)
    if shared.hp_mp_check_thread:
        shared.hp_mp_check_thread = stop_hp_mp_check(shared.hp_mp_check_thread)


def start_threads():
    shared.auto_attack_thread = start_auto_attack(shared.config)
    shared.hp_mp_check_thread = start_hp_mp_check(shared.config)


if __name__ == "__main__":
    start_global_key_listener()
    create_gui()
