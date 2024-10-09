import threading
import time

import pydirectinput

from utils.logger import get_logger

logger = get_logger(__name__)
stop_auto_attack_event = threading.Event()


def auto_attack_function(config: dict) -> None:
    attack_settings = config["attack_settings"]
    while config['auto_attack_toggle'] and not stop_auto_attack_event.is_set():
        # Continuously press 'Z' to target
        pydirectinput.press('z')
        time.sleep(0.1)

        # Continuously press 'R' if enabled
        if attack_settings.get("enable_basic_attack", False):
            pydirectinput.press('r')

        # Execute selected skills
        for skill in attack_settings.get("skills", []):
            if skill["enabled"]:
                logger.info(f"Attempting skill: {skill['name']}")
                # Switch to the specified skill bar
                pydirectinput.press(skill["skill_bar"])
                # Press the skill slot key
                pydirectinput.press(skill["slot"])
                # Continuously press 'R' if enabled
                if attack_settings.get("enable_basic_attack", False):
                    pydirectinput.press('r')

            # Increase delay between skill activations
            time.sleep(0.2)


def start_auto_attack(config: dict) -> threading.Thread | None:
    try:
        if config['auto_attack_toggle']:
            stop_auto_attack_event.clear()
            attack_thread = threading.Thread(target=auto_attack_function, args=(config,))
            attack_thread.start()
            logger.info("Auto-attack started.")
            return attack_thread
        else:
            return None
    except Exception as e:
        logger.error(f"Exception in start_auto_attack {e}")
        return None


def stop_auto_attack(thread: threading.Thread) -> None:
    stop_auto_attack_event.set()
    thread.join()
    logger.info("Auto-attack stopped.")
    return None
