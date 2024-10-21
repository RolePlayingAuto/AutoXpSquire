import threading
import time

import pydirectinput

from utils.logger import get_logger
import utils.shared as shared

logger = get_logger(__name__)


def auto_attack_function(config: dict) -> None:
    attack_settings = config["attack_settings"]
    enabled_skills = [skill for skill in attack_settings.get("skills", []) if skill["enabled"]]
    while config['auto_attack_toggle'] and not shared.stop_auto_attack_event.is_set():
        # Continuously press 'Z' to target
        pydirectinput.press('z')
        time.sleep(0.01)

        # Execute selected skills
        for skill in enabled_skills:
            logger.info(f"Attempting skill: {skill['name']}")
            pydirectinput.press(skill["skill_bar"])
            pydirectinput.press(skill["slot"])
            # Continuously press 'R' if enabled
            if attack_settings.get("enable_basic_attack", False):
                pydirectinput.press('r')
            pydirectinput.press('z')
            # Increase delay between skill activations
            time.sleep(0.15)
            shared.stop_auto_attack_event.wait()


def start_auto_attack(config: dict) -> threading.Thread | None:
    try:
        if config['auto_attack_toggle']:
            shared.stop_auto_attack_event.clear()
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
    shared.stop_auto_attack_event.set()
    thread.join()
    logger.info("Auto-attack stopped.")
    return None
