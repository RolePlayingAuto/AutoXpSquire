import cv2
import numpy as np
import pydirectinput
import time
import threading

from PIL import ImageGrab


# Function to calculate bar percentage based on color
def calculate_bar_percentage(region, target_color_bgr):
    screenshot = ImageGrab.grab(bbox=region)
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color ranges for the bars
    if target_color_bgr == [0, 0, 255]:  # Red HP bar
        lower_color = np.array([0, 70, 50])
        upper_color = np.array([10, 255, 255])
    elif target_color_bgr == [255, 0, 0]:  # Blue MP bar
        lower_color = np.array([110, 70, 50])
        upper_color = np.array([130, 255, 255])

    mask = cv2.inRange(hsv_image, lower_color, upper_color)

    # Sum up pixels vertically to project on the x-axis
    projection = np.sum(mask, axis=0)
    filled_indices = np.where(projection > 0)[0]

    if filled_indices.size == 0:
        return 0

    filled_length = filled_indices[-1] - filled_indices[0]
    total_length = mask.shape[1]

    percentage = ((filled_length + 1) / total_length) * 100
    return percentage


# Function to read HP and MP values
def read_hp_mp(hp_bar_position, mp_bar_position):
    if hp_bar_position and mp_bar_position:
        hp_percentage = calculate_bar_percentage(hp_bar_position, [0, 0, 255])  # Red HP bar
        mp_percentage = calculate_bar_percentage(mp_bar_position, [255, 0, 0])  # Blue MP bar

        print(f"HP Percentage: {hp_percentage:.2f}%")
        print(f"MP Percentage: {mp_percentage:.2f}%")

        return hp_percentage, mp_percentage
    return None, None


# Function to press the potion key
def use_potion(key):
    pydirectinput.press(key)


def check_hp_mp(hp_threshold, mp_threshold, hp_bar_position, mp_bar_position, hp_pot_key, mp_pot_key, is_running_func):
    while is_running_func():
        hp_percentage, mp_percentage = read_hp_mp(hp_bar_position, mp_bar_position)

        if hp_percentage is not None and mp_percentage is not None:
            if hp_percentage <= hp_threshold:
                use_potion(hp_pot_key)

            if mp_percentage <= mp_threshold:
                use_potion(mp_pot_key)
        time.sleep(0.5)  # Reduced sleep time for faster response


# Start HP/MP check thread
def start_hp_mp_check(config):
    if config.hp_mp_check:
        hp_mp_thread = threading.Thread(
            target=check_hp_mp,
            args=(config.hp_threshold, config.mp_threshold, config.hp_bar_position, config.mp_bar_position, config.hp_pot_key, config.mp_pot_key, lambda: hp_mp_check)
        )
        hp_mp_thread.start()
        print("HP/MP check started.")
        return hp_mp_thread
    else:
        return None


# Stop HP/MP check
def stop_hp_mp_check(hp_mp_thread):
    global hp_mp_check
    hp_mp_thread.join()
    hp_mp_check = False
    print("HP/MP check stopped.")
    return None
