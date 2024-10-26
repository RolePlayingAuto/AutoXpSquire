import os
import threading
import time

import cv2
import numpy as np
import pydirectinput
from PIL import ImageGrab

import utils.shared as shared
from utils.logger import get_logger

logger = get_logger(__name__)


def start_auto_buff(config: dict) -> threading.Thread | None:
    if config['auto_buff']:
        shared.stop_auto_buff_event.clear()
        buff_thread = threading.Thread(target=buff_loop, args=(config,), daemon=True)
        buff_thread.start()
        logger.info("Auto-buff started.")
        return buff_thread
    else:
        return None


def stop_auto_buff(buff_thread: threading.Thread) -> None:
    shared.stop_auto_buff_event.set()
    buff_thread.join()
    logger.info("Auto-buff stopped.")
    return None


def buff_loop(config: dict) -> None:
    buff_skills = [skill for skill in config["attack_settings"]["skills"]
                   if skill["buff"] and skill["enabled"]]

    if not buff_skills:
        logger.info("No buff skills configured.")
        return

    buff_coordinates = config.get("buff_coordinates")
    if not buff_coordinates:
        logger.error("Buff coordinates not set.")
        return

    # Initialize last cast times for each buff skill
    last_cast_times = {skill["name"]: 0 for skill in buff_skills}

    while not shared.stop_auto_buff_event.is_set():
        current_time = time.time()  # Current time in seconds

        for skill in buff_skills:
            # Get the cooldown for the skill (in milliseconds)
            cooldown_s = skill.get("cooldown", 0)
            # Check if cooldown period has passed since last cast
            time_since_last_cast = current_time - last_cast_times[skill["name"]]
            if time_since_last_cast < cooldown_s:
                # Cooldown period has not passed; skip checking this buff
                continue

            # Construct the icon path
            icon_path = f"static/{config['attack_settings']['selected_class'].
                                  lower()}_{skill['subclass'].lower()}_{skill['name'].lower()}.png"
            if not os.path.exists(icon_path):
                logger.error(f"Icon not found for skill {skill['name']} at {icon_path}")
                continue

            # Capture screenshot of the buff area
            x1, y1, x2, y2 = buff_coordinates
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

            # Load the buff icon
            template = cv2.imread(icon_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                logger.error(f"Failed to load template image for {skill['name']}")
                continue
            # Perform template matching
            res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            threshold = 0.75

            if max_val < threshold:
                logger.debug(f"Buff {skill['name']} is missing (max_val={max_val}).")
                shared.resume_attack_event.clear()
                logger.info(f"Casting buff {skill['name']}")
                pydirectinput.press(skill["skill_bar"])
                pydirectinput.press(skill["slot"])
                last_cast_times[skill["name"]] = time.time()
                time.sleep(2)
                shared.resume_attack_event.set()
            else:
                logger.debug(f"Buff {skill['name']} is active.")

    time.sleep(0.5)
