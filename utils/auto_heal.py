import threading
import time
from typing import Tuple

import pydirectinput

import utils.shared as shared
from utils.hp_mp import read_hp_mp
from utils.logger import get_logger

logger = get_logger(__name__)


def start_auto_heal(config: dict) -> threading.Thread | None:
    if config['auto_heal']:
        shared.stop_auto_heal_event.clear()
        heal_thread = threading.Thread(target=heal_loop, args=(config,), daemon=True)
        heal_thread.start()
        logger.info("Auto-heal started.")
        return heal_thread
    else:
        return None


def stop_auto_heal(heal_thread: threading.Thread) -> None:
    shared.stop_auto_heal_event.set()
    heal_thread.join()
    logger.info("Auto-heal stopped.")
    return None


def heal_loop(config: dict) -> None:
    heal_skills = [skill for skill in config["attack_settings"]["skills"]
                   if skill["heal"] and skill["enabled"]]

    if not heal_skills:
        logger.info("No heal skills configured.")
        return

    # Initialize last cast times for each heal skill
    last_cast_times = {skill["name"]: 0.0 for skill in heal_skills}

    while not shared.stop_auto_heal_event.is_set():
        current_time = time.time()  # Current time in seconds

        if not heal_needed(config["heal_threshold"], config["hp_bar_position"]):
            time.sleep(0.5)
            continue

        for skill in heal_skills:
            # Get the cooldown for the skill (in milliseconds)
            cooldown_s = skill.get("cooldown", 0)
            cast_time_s = skill.get('cast_time', 0) / 1000.0
            # Check if cooldown period has passed since last cast
            time_since_last_cast = current_time - last_cast_times[skill["name"]]
            if time_since_last_cast < cooldown_s:
                # Cooldown period has not passed; skip checking this heal
                continue
            if not heal_needed(config["heal_threshold"], config["hp_bar_position"]):
                time.sleep(0.5)
                continue
            logger.debug(f"Heal needed, casting {skill['name']}")
            shared.resume_attack_event.clear()
            pydirectinput.press(skill["skill_bar"])
            pydirectinput.press(skill["slot"])
            last_cast_times[skill["name"]] = time.time()
            time.sleep(cast_time_s)
            shared.resume_attack_event.set()
            time.sleep(0.1)


def heal_needed(heal_threshold: int, hp_bar_position: Tuple[int, int, int, int]) -> bool:
    hp_percentage, _ = read_hp_mp(hp_bar_position, hp_bar_position)
    if hp_percentage is not None and hp_percentage <= heal_threshold:
        return True
    else:
        return False
