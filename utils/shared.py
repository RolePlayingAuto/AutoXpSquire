'''To implement shared variables between different modules'''
from threading import Event, Thread
from typing import Optional

from utils.loader import load_config

# Threads
auto_attack_thread: Optional[Thread] = None
hp_mp_check_thread: Optional[Thread] = None
buff_thread: Optional[Thread] = None

# Thread stop events
stop_auto_attack_event = Event()
stop_hp_mp_event = Event()
stop_auto_buff_event = Event()
resume_attack_event = Event()

config = load_config()
