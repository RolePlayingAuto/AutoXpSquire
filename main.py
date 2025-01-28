from pynput import keyboard

import app.shared as shared
from app.auto_attack import start_auto_attack, stop_auto_attack
from app.auto_buff import start_auto_buff, stop_auto_buff
from app.auto_heal import start_auto_heal, stop_auto_heal
from app.gui import create_gui
from app.hp_mp import start_hp_mp_check, stop_hp_mp_check
from utils.loader import load_config
from utils.logger import get_logger

logger = get_logger(__name__)


# ESC and F11 key listener
def on_press_events_toggle(key: keyboard.Key) -> None:
    try:
        if key == keyboard.Key.esc:  # Stop the bot
            stop_threads()
            logger.info("Bot Stopped")
        elif key == keyboard.Key.f11:  # Start the bot
            start_threads()
            logger.info("Bot Started")
    except AttributeError as a:
        logger.error(f"on_press_event failed: {a}")
        pass
    except Exception as e:
        logger.error(f"on_press_event failed: {e}")


def start_global_key_listener() -> None:
    listener = keyboard.Listener(on_press=on_press_events_toggle)
    shared.config = load_config()
    listener.start()


def stop_threads() -> None:
    if shared.auto_attack_thread:
        stop_auto_attack(shared.auto_attack_thread)
        shared.auto_attack_thread = None
    if shared.hp_mp_check_thread:
        stop_hp_mp_check(shared.hp_mp_check_thread)
        shared.hp_mp_check_thread = None
    if shared.buff_thread:
        stop_auto_buff(shared.buff_thread)
        shared.buff_thread = None
    if shared.heal_thread:
        stop_auto_heal(shared.heal_thread)
        shared.heal_thread = None


def start_threads() -> None:
    shared.auto_attack_thread = start_auto_attack(shared.config)
    shared.hp_mp_check_thread = start_hp_mp_check(shared.config)
    shared.buff_thread = start_auto_buff(shared.config)
    shared.heal_thread = start_auto_heal(shared.config)


if __name__ == "__main__":
    start_global_key_listener()
    create_gui()
