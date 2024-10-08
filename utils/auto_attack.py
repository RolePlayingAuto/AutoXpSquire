import threading
import time

import pydirectinput

from utils.logger import get_logger

logger = get_logger(__name__)
auto_attack = False


def auto_attack_function(config: dict) -> None:
    attack_settings = config["attack_settings"]
    while auto_attack:
        if config["target_window"]:
            config["target_window"].activate()

            # Continuously press 'Z' to target
            pydirectinput.press('z')
            time.sleep(0.1)

            # Continuously press 'R' if enabled
            if attack_settings.get("enable_basic_attack", False):
                pydirectinput.press('r')
                time.sleep(0.1)

            # Execute selected skills
            for skill in attack_settings.get("skills", []):
                if skill["enabled"]:
                    logger.info(f"Attempting skill: {skill['name']}")
                    # Switch to the specified skill bar
                    pydirectinput.press(skill["skill_bar"])
                    time.sleep(0.1)
                    # Press the skill slot key
                    pydirectinput.press(skill["slot"])
                    time.sleep(0.2)
                    # Continuously press 'R' if enabled
                    if attack_settings.get("enable_basic_attack", False):
                        pydirectinput.press('r')
                        time.sleep(0.1)

            # Increase delay between skill activations
            time.sleep(1)
        else:
            logger.error("Target window not found.")
            break


def start_auto_attack(config: dict) -> threading.Thread | None:
    try:
        if config['auto_attack_toggle']:
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
    thread.join()
    logger.info("Auto-attack stopped.")
    return None
