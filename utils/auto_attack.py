import threading
import time
from difflib import SequenceMatcher

import easyocr
import numpy as np
import pydirectinput
from PIL import ImageGrab, Image

import utils.shared as shared
from utils.logger import get_logger

reader = easyocr.Reader(['en'], gpu=True)

logger = get_logger(__name__)


def auto_attack_function(config: dict) -> None:
    attack_settings = config["attack_settings"]
    enabled_skills = [skill for skill in attack_settings.get("skills", [])
                      if skill["enabled"] and not skill["buff"] and not skill["heal"]]
    shared.resume_attack_event.set()
    monster_names = [name.lower() for name in config["attack_settings"].get("monster_names", [])]
    while config['auto_attack_toggle'] and not shared.stop_auto_attack_event.is_set():
        if not shared.resume_attack_event.is_set():
            time.sleep(0.05)
            continue
        auto_target(config)

        if config["attack_settings"].get("monster_name_coord"):
            if monster_names:
                detected_text = ocr_extract_text(config["attack_settings"]["monster_name_coord"], monster_names)
                logger.info(f"Detected text: {detected_text}")

                if detected_text not in monster_names:
                    logger.info(f"{detected_text} not in monster list, skipping this target.")
                    continue

        basic_attack(config)
        # Execute selected skills
        for skill in enabled_skills:
            if shared.stop_auto_attack_event.is_set():
                break
            if not shared.resume_attack_event.is_set():
                time.sleep(0.05)
                continue
            auto_target(config)

            if config["attack_settings"].get("monster_name_coord"):
                if monster_names:
                    detected_text = ocr_extract_text(config["attack_settings"]["monster_name_coord"], monster_names)
                    logger.info(f"Detected text: {detected_text}")

                    if detected_text not in monster_names:
                        logger.info(f"{detected_text} not in monster list, skipping this target.")
                        continue

            basic_attack(config)
            use_skill(skill)
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


def ocr_extract_text(region: tuple, monster_names: list) -> str:
    # Capture the screen region
    screenshot = ImageGrab.grab(bbox=region)

    # Convert the screenshot to a numpy array format (required by EasyOCR)
    screenshot_np = np.array(screenshot)

    # Use EasyOCR to extract text along with their confidence scores
    result = reader.readtext(
        screenshot_np,
        allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ][)(',
        detail=1,
        adjust_contrast=0.0,
        contrast_ths=0.0,
        paragraph=False,
        decoder='greedy',
        beamWidth=1,
        batch_size=1,
        workers=0,
        mag_ratio=1.0
    )

    # Find the detection with the highest confidence score
    best_text = ""
    highest_confidence = 0.0

    for detection in result:
        text, confidence = detection[1], detection[2]
        if confidence > highest_confidence:
            best_text = text
            highest_confidence = confidence

    # Clean up the detected text to keep only alphabetic characters
    detected_text = best_text.lower()

    # Find the best match from the monster_names list with at least 80% similarity
    best_match = ""
    best_match_score = 0.0

    for monster_name in monster_names:
        # Calculate similarity ratio between detected_text and monster_name
        similarity_score = SequenceMatcher(None, detected_text, monster_name.lower()).ratio()
        if similarity_score > best_match_score and similarity_score >= 0.8:
            best_match = monster_name
            best_match_score = similarity_score

    # Return the best match if it meets the 80% threshold, otherwise return an empty string
    return best_match if best_match_score >= 0.8 else detected_text
