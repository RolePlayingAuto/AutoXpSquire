'''To implement shared variables between different modules'''
from utils.loader import load_config

auto_attack_thread = None
hp_mp_check_thread = None
config = load_config()
