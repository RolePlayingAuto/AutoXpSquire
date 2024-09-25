import pydirectinput
import threading
import time


def auto_attack_function():
    global config
    global auto_attack, attack_settings
    while auto_attack:
        if config.target_window:
            config.target_window.activate()

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
                    print(f"Attempting skill: {skill['name']}")
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
            time.sleep(1)  # Approximately 1 second delay
        else:
            print("Target window not found.")
            break


def start_auto_attack():
    global auto_attack, attack_thread
    if not auto_attack:
        auto_attack = True
        attack_thread = threading.Thread(target=auto_attack_function)
        attack_thread.start()
        print("Auto-attack started.")


def stop_auto_attack():
    global auto_attack
    if auto_attack:
        auto_attack = False
        print("Auto-attack stopped.")