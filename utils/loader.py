from yaml import safe_load


def load_config(config_file="config/config.yml"):
    with open(config_file, 'r') as file:
        config = safe_load(file)
    
    # Extract values, load default if non existent
    window_name = config.get("window_name", "Game Window Name")
    
    hp_threshold = config.get("hp_threshold", 50)
    mp_threshold = config.get("mp_threshold", 50)
    hp_pot_key = config.get("hp_pot_key", '1')
    mp_pot_key = config.get("mp_pot_key", '2')
    
    hp_bar_position = config.get("hp_bar_position", None)
    mp_bar_position = config.get("mp_bar_position", None)

    attack_settings = config.get("attack_settings", {})
    enable_basic_attack = attack_settings.get("enable_basic_attack", False)
    selected_class = attack_settings.get("selected_class", None)
    skills = attack_settings.get("skills", [])

    class_options = config.get("class_options", ["Rogue", "Mage", "Priest", "Warrior"])
    
    return {
        "window_name": window_name,
        "hp_threshold": hp_threshold,
        "mp_threshold": mp_threshold,
        "hp_pot_key": hp_pot_key,
        "mp_pot_key": mp_pot_key,
        "hp_bar_position": hp_bar_position,
        "mp_bar_position": mp_bar_position,
        "attack_settings": {
            "enable_basic_attack": enable_basic_attack,
            "selected_class": selected_class,
            "skills": skills
        },
        "class_options": class_options
    }


def load_skill_data(skill_file="config/skilldata_config.yml"):
    with open(skill_file, 'r') as file:
        skill_data = safe_load(file)
    
    return skill_data
