import os

import yaml
from yaml import dump, safe_load


def load_config(config_file="config/config.yml"):
    try:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found.")
        # Using yaml.Loader to allow python-specific types like !!python/tuple
        with open(config_file, 'r') as file:
            config = yaml.load(file, Loader=yaml.Loader)

        # Extract values, load default if non-existent
        window_name = config.get("window_name", "Game Window Name")
        hp_threshold = config.get("hp_threshold", 50)
        mp_threshold = config.get("mp_threshold", 50)
        hp_pot_key = config.get("hp_pot_key", '1')
        mp_pot_key = config.get("mp_pot_key", '2')
        hp_mp_check = config.get("hp_mp_check", False)
        auto_attack_toggle = config.get("auto_attack_toggle", False)

        hp_bar_position = config.get("hp_bar_position", None)
        mp_bar_position = config.get("mp_bar_position", None)

        attack_settings = config.get("attack_settings", {})
        enable_basic_attack = attack_settings.get("enable_basic_attack", False)
        selected_class = attack_settings.get("selected_class", None)
        skills = attack_settings.get("skills", [])

        class_options = config.get("class_options", ["Rogue", "Mage", "Priest", "Warrior"])

        # Return the full configuration as a dictionary
        return {
            "window_name": window_name,
            "hp_threshold": hp_threshold,
            "mp_threshold": mp_threshold,
            "hp_pot_key": hp_pot_key,
            "mp_pot_key": mp_pot_key,
            "hp_mp_check": hp_mp_check,
            "auto_attack_toggle": auto_attack_toggle,
            "hp_bar_position": hp_bar_position,
            "mp_bar_position": mp_bar_position,
            "attack_settings": {
                "enable_basic_attack": enable_basic_attack,
                "selected_class": selected_class,
                "skills": skills
            },
            "class_options": class_options
        }

    except FileNotFoundError:
        print(f"Config file {config_file} not found.")
        return {}
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {}


def load_skill_data(skill_file="config/skilldata_config.yml"):
    try:
        with open(skill_file, 'r') as file:
            skill_data = safe_load(file)
        return skill_data
    except FileNotFoundError:
        print(f"Skill data file {skill_file} not found.")
        return {}
    except Exception as e:
        print(f"Error loading skill data: {e}")
        return {}


def write_config_to_file(config, filename="config/config.yml"):
    try:
        with open(filename, 'w') as file:
            dump(config, file, default_flow_style=False)
    except FileNotFoundError:
        print(f"Write config to file {filename} not found.")
        return {}
    except Exception as e:
        print(f"Error Writing config file: {e}")
        return {}
