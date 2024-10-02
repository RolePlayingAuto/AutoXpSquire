from pynput import keyboard

from utils.auto_attack import start_auto_attack, stop_auto_attack
from utils.gui import create_gui
from utils.hp_mp import start_hp_mp_check, stop_hp_mp_check
from utils.loader import load_config

config = load_config()
hp_mp_thread = None
auto_attack_thread = None

# ESC and F11 key listener
def on_press_events_toggle(key):
    global config, hp_mp_thread, auto_attack_thread
    try:
        if key == keyboard.Key.esc:
            if auto_attack_thread:
                auto_attack_thread = stop_auto_attack(auto_attack_thread)
            if hp_mp_thread:
                hp_mp_thread = stop_hp_mp_check(hp_mp_thread)
            print("Bot Stopped")
        elif key == keyboard.Key.f11:
            auto_attack_thread = start_auto_attack(config)
            hp_mp_thread = start_hp_mp_check(config)
            print("Bot Started")
    except AttributeError:
        pass
    except Exception as e:
        print(f"on_press_event failed: {e}")
# Start the key listener
def start_global_key_listener():
    global config
    listener = keyboard.Listener(on_press=on_press_events_toggle)
    config = load_config()
    listener.start()
if __name__ == "__main__":
    start_global_key_listener()
    create_gui()
