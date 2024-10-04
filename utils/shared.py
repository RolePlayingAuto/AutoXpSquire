'''To implement shared variables between different modules'''
from threading import Thread
from typing import Optional

from utils.loader import load_config

auto_attack_thread: Optional[Thread] = None
hp_mp_check_thread: Optional[Thread] = None
config = load_config()
