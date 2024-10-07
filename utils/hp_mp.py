import threading
import time
from typing import Any, List, Literal, Tuple

import cv2
import numpy as np
import pydirectinput
from PIL import ImageGrab

from utils.logger import get_logger

logger = get_logger(__name__)
stop_hp_mp_event = threading.Event()


def calculate_bar_percentage(region: Tuple[int, int, int, int],
                             target_color_bgr: List[int]) -> Any | Literal[0]:
    # Capture the region from the screen
    screenshot = ImageGrab.grab(bbox=region)
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Convert to HSV for better color filtering
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color ranges for the bars
    if target_color_bgr == [0, 0, 255]:  # Red HP bar
        lower_color = np.array([0, 70, 50])
        upper_color = np.array([10, 255, 255])
    elif target_color_bgr == [255, 0, 0]:  # Blue MP bar
        lower_color = np.array([110, 70, 50])
        upper_color = np.array([130, 255, 255])

    # Create a mask that isolates the target color range
    mask = cv2.inRange(hsv_image, lower_color, upper_color)

    # Sum up the pixels vertically to project on the x-axis
    projection = np.sum(mask, axis=0)
    filled_indices = np.where(projection > 0)[0]

    if filled_indices.size == 0:
        return 0

    filled_length = filled_indices[-1] - filled_indices[0]
    total_length = mask.shape[1]

    percentage = ((filled_length + 1) / total_length) * 100
    return percentage


def read_hp_mp(hp_bar_position: Tuple[int, int, int, int],
               mp_bar_position: Tuple[int, int, int, int]) -> Tuple[Any | Literal[0], Any | Literal[0]]:
    logger.info(f"hp bar position {hp_bar_position} mp bar positon {mp_bar_position}")
    if hp_bar_position and mp_bar_position:
        hp_percentage = calculate_bar_percentage(hp_bar_position, [0, 0, 255])  # Red HP bar
        mp_percentage = calculate_bar_percentage(mp_bar_position, [255, 0, 0])  # Blue MP bar

        logger.info(f"HP Percentage: {hp_percentage:.2f}%")
        logger.info(f"MP Percentage: {mp_percentage:.2f}%")

        return hp_percentage, mp_percentage
    return None, None


# Function to press the potion key
def use_potion(key: Any) -> None:
    pydirectinput.press(key)


def check_hp_mp(hp_threshold: int, mp_threshold: int,
                hp_bar_position: Tuple[int, int, int, int],
                mp_bar_position: Tuple[int, int, int, int],
                hp_pot_key: int, mp_pot_key: int) -> None:
    while not stop_hp_mp_event.is_set():
        hp_percentage, mp_percentage = read_hp_mp(hp_bar_position, mp_bar_position)

        if hp_percentage is not None and mp_percentage is not None:
            if hp_percentage <= hp_threshold:
                use_potion(hp_pot_key)

            if mp_percentage <= mp_threshold:
                use_potion(mp_pot_key)
        time.sleep(0.5)  # Reduced sleep time for faster response


# Start HP/MP check thread
def start_hp_mp_check(config: dict) -> threading.Thread | None:
    try:
        if config['hp_mp_check']:
            stop_hp_mp_event.clear()
            hp_mp_thread = threading.Thread(
                target=check_hp_mp,
                args=(config["hp_threshold"], config["mp_threshold"], config["hp_bar_position"],
                      config["mp_bar_position"], config["hp_pot_key"], config["mp_pot_key"])
            )
            hp_mp_thread.start()
            logger.info("HP/MP check started.")
            return hp_mp_thread
        else:
            return None
    except Exception as e:
        logger.error(f"Exception in start_hp_mp_check {e}")
        return None


# Stop HP/MP check
def stop_hp_mp_check(hp_mp_thread: threading.Thread) -> None:
    stop_hp_mp_event.set()
    hp_mp_thread.join()
    logger.info("HP/MP check stopped.")
    return None
