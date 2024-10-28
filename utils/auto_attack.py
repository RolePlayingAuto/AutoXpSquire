import threading
import time

import pydirectinput

import utils.shared as shared
from utils.logger import get_logger

logger = get_logger(__name__)


def auto_attack_function(config: dict) -> None:
    attack_settings = config["attack_settings"]
    enabled_skills = [skill for skill in attack_settings.get("skills", [])
                      if skill["enabled"] and not skill["buff"] and not skill["heal"]]
    shared.resume_attack_event.set()
    while config['auto_attack_toggle'] and not shared.stop_auto_attack_event.is_set():
        if not shared.resume_attack_event.is_set():
            time.sleep(0.1)
            continue
        auto_target(config)
        basic_attack(config)
        # Execute selected skills
        for skill in enabled_skills:
            if shared.stop_auto_attack_event.is_set():
                break
            if not shared.resume_attack_event.is_set():
                time.sleep(0.1)
                continue
            auto_target(config)
            basic_attack(config)
            use_skill(skill)
            auto_target(config)
            basic_attack(config)
            # Increase delay between skill activations
            time.sleep(0.1)


def start_auto_attack(config: dict) -> threading.Thread | None:
    try:
        if config['auto_attack_toggle']:
            shared.stop_auto_attack_event.clear()
            attack_thread = threading.Thread(target=auto_attack_function, args=(config,), daemon=True)
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


def auto_target(config: dict) -> None:
    if config["attack_settings"]["enable_auto_target"]:
        pydirectinput.press(config["attack_settings"]["auto_target_key"])


def basic_attack(config: dict) -> None:
    if config["attack_settings"]["enable_basic_attack"]:
        pydirectinput.press(config["attack_settings"]["basic_attack_key"])


def use_skill(skill: dict) -> None:
    logger.info(f"Attempting skill: {skill['name']}")
    pydirectinput.press(skill["skill_bar"])
    pydirectinput.press(skill["slot"])
