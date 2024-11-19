import os
import time
import tkinter as tk
from tkinter import messagebox, ttk  # noqa: F401
from typing import Any, Callable, Optional, Tuple

import pygetwindow as gw

import utils.shared as shared
from utils.auto_attack import start_auto_attack, stop_auto_attack
from utils.auto_buff import start_auto_buff, stop_auto_buff
from utils.hp_mp import start_hp_mp_check, stop_hp_mp_check
from utils.loader import load_skill_data, write_config_to_file
from utils.logger import get_logger

logger = get_logger(__name__)
# Globals
target_window = None


def create_gui() -> None:
    skill_data = load_skill_data()
    window = tk.Tk()
    window.title("AutoXpSquire")
    window.geometry("800x800")  # Adjusted for better initial size
    tab_control = ttk.Notebook(window)
    control_tab = ttk.Frame(tab_control)
    settings_tab = ttk.Frame(tab_control)
    skill_settings_tab = ttk.Frame(tab_control)
    tab_control.add(control_tab, text="Control")
    tab_control.add(settings_tab, text="Settings")
    tab_control.add(skill_settings_tab, text="Skill Settings")
    tab_control.pack(expand=1, fill="both")

    # Control Tab
    tk.Label(control_tab, text="AutoXpSquire Bot Control", font=("Arial", 14, "bold")).pack(pady=10)
    control_frame = tk.Frame(control_tab)
    control_frame.pack(fill="both", expand=True)

    # Configure columns for better alignment
    control_frame.columnconfigure(0, weight=1)
    control_frame.columnconfigure(1, weight=1)

    # Use grid layout for better alignment
    row = 0
    tk.Label(
        control_frame,
        text="Game Window Name:",
        font=("Arial", 10, "bold")
    ).grid(row=row, column=0, sticky='e', padx=5, pady=(10, 5))
    window_name_entry = tk.Entry(control_frame)
    window_name_entry.insert(0, shared.config.get("window_name", ""))
    window_name_entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
    row += 1

    # Auto-attack checkbox
    attack_var = tk.BooleanVar()
    attack_checkbox = tk.Checkbutton(
        control_frame,
        text="Start Auto-Attack",
        variable=attack_var,
        command=lambda: config_variable_setter(shared.config, attack_var.get(), "auto_attack_toggle")
    )
    attack_var.set(shared.config.get("auto_attack_toggle", False))
    attack_checkbox.grid(row=row, column=0, columnspan=2, sticky='', padx=5, pady=5)
    row += 1

    # HP and MP check checkbox
    hp_mp_check_var = tk.BooleanVar()
    hp_mp_checkbox = tk.Checkbutton(
        control_frame,
        text="Enable HP/MP Check",
        variable=hp_mp_check_var,
        command=lambda: config_variable_setter(shared.config, hp_mp_check_var.get(), "hp_mp_check")
    )
    hp_mp_check_var.set(shared.config.get("hp_mp_check", False))
    hp_mp_checkbox.grid(row=row, column=0, columnspan=2, sticky='', padx=5, pady=5)
    row += 1

    # Auto Buff checkbox
    auto_buff_var = tk.BooleanVar()
    auto_buff_checkbox = tk.Checkbutton(
        control_frame,
        text="Enable Auto Buff",
        variable=auto_buff_var,
        command=lambda: config_variable_setter(shared.config, auto_buff_var.get(), "auto_buff")
    )
    auto_buff_var.set(shared.config.get("auto_buff", False))
    auto_buff_checkbox.grid(row=row, column=0, columnspan=2, sticky='', padx=5, pady=5)
    row += 1

    # Auto Heal checkbox
    auto_heal_var = tk.BooleanVar()
    auto_heal_checkbox = tk.Checkbutton(
        control_frame,
        text="Enable Auto Heal",
        variable=auto_heal_var,
        command=lambda: config_variable_setter(shared.config, auto_heal_var.get(), "auto_heal")
    )
    auto_heal_var.set(shared.config.get("auto_heal", False))
    auto_heal_checkbox.grid(row=row, column=0, columnspan=2, sticky='', padx=5, pady=5)
    row += 1

    def config_variable_setter(config: dict, variable: Any, variable_name: str) -> None:
        config[variable_name] = variable
        logger.info(f"Config value {variable_name} has been set to: {variable}")

    def start_bot() -> None:
        global target_window
        target_window = find_window(shared.config["window_name"])

        if target_window is None:
            logger.info(f"{shared.config['window_name']} window not found!")
            return

        # Bring the game window to the front
        target_window.activate()
        time.sleep(0.3)
        if attack_var.get():
            shared.auto_attack_thread = start_auto_attack(shared.config)
        if hp_mp_check_var.get():
            shared.hp_mp_check_thread = start_hp_mp_check(shared.config)
        if auto_buff_var.get():
            shared.buff_thread = start_auto_buff(shared.config)
        logger.info("Bot started.")

    def stop_bot() -> None:
        if shared.auto_attack_thread:
            logger.info("Auto attack thread found, stopping auto attack")
            stop_auto_attack(shared.auto_attack_thread)
            shared.auto_attack_thread = None
        if shared.hp_mp_check_thread:
            logger.info("hp_mp_check thread found, stopping hp_mp_check")
            stop_hp_mp_check(shared.hp_mp_check_thread)
            shared.hp_mp_check_thread = None
        if shared.buff_thread:
            logger.info("auto_buff thread found, stopping auto_buff")
            stop_auto_buff(shared.buff_thread)
            shared.buff_thread = None
        logger.info("Bot stopped")

    # Start and Stop buttons
    start_button = tk.Button(control_frame, text="Start Bot", command=start_bot)
    start_button.grid(row=row, column=0, padx=5, pady=5, sticky='e')
    stop_button = tk.Button(control_frame, text="Stop Bot", command=stop_bot)
    stop_button.grid(row=row, column=1, padx=5, pady=5, sticky='w')
    row += 1

    # Settings Tab with sub-tabs
    settings_notebook = ttk.Notebook(settings_tab)
    settings_notebook.pack(expand=1, fill="both")

    hp_mp_tab = ttk.Frame(settings_notebook)
    attack_settings_tab = ttk.Frame(settings_notebook)
    buff_settings_tab = ttk.Frame(settings_notebook)
    heal_settings_tab = ttk.Frame(settings_notebook)
    other_settings_tab = ttk.Frame(settings_notebook)
    settings_notebook.add(hp_mp_tab, text="HP/MP")
    settings_notebook.add(attack_settings_tab, text="Attack Settings")
    settings_notebook.add(buff_settings_tab, text="Buff Settings")
    settings_notebook.add(heal_settings_tab, text="Heal Settings")
    settings_notebook.add(other_settings_tab, text="Other Settings")

    # HP/MP Tab content
    tk.Label(hp_mp_tab, text="HP/MP Settings", font=("Arial", 12, "bold")).pack(pady=10)
    hp_mp_frame = tk.Frame(hp_mp_tab)
    hp_mp_frame.pack(fill="both", expand=True)

    # Configure columns
    hp_mp_frame.columnconfigure(0, weight=1)
    hp_mp_frame.columnconfigure(1, weight=1)

    row = 0
    set_hp_button = tk.Button(
        hp_mp_frame,
        text="Select HP Bar Region",
        font=("Arial", 10, "bold"),
        command=lambda: select_region(update_hp_bar_position)
    )
    set_hp_button.grid(row=row, column=0, columnspan=2, sticky='', padx=5, pady=5)
    row += 1

    set_mp_button = tk.Button(
        hp_mp_frame,
        text="Select MP Bar Region",
        font=("Arial", 10, "bold"),
        command=lambda: select_region(update_mp_bar_position)
    )
    set_mp_button.grid(row=row, column=0, columnspan=2, sticky='', padx=5, pady=5)
    row += 1

    hp_coord_label = tk.Label(hp_mp_frame, text="HP Bar Coordinates: Not Selected", font=("Arial", 10, "bold"))
    hp_coord_label.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    row += 1

    mp_coord_label = tk.Label(hp_mp_frame, text="MP Bar Coordinates: Not Selected", font=("Arial", 10, "bold"))
    mp_coord_label.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    row += 1

    if "hp_bar_position" in shared.config:
        hp_coord_label.config(text=f"HP Bar Coordinates: {shared.config['hp_bar_position']}")

    if "mp_bar_position" in shared.config:
        mp_coord_label.config(text=f"MP Bar Coordinates: {shared.config['mp_bar_position']}")

    # HP and MP coordinate update functions
    def update_hp_bar_position(region: Tuple[int, int, int, int]) -> None:
        shared.config["hp_bar_position"] = region
        hp_coord_label.config(text=f"HP Bar Coordinates: {region}")

    def update_mp_bar_position(region: Tuple[int, int, int, int]) -> None:
        shared.config["mp_bar_position"] = region
        mp_coord_label.config(text=f"MP Bar Coordinates: {region}")

    # Settings frame for thresholds and keys
    settings_frame = tk.Frame(hp_mp_frame)
    settings_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
    row += 1

    # Configure columns in settings_frame
    settings_frame.columnconfigure(0, weight=1)
    settings_frame.columnconfigure(1, weight=2)
    settings_frame.columnconfigure(2, weight=1)
    settings_frame.columnconfigure(3, weight=2)

    tk.Label(settings_frame, text="HP Pot Threshold (%):", font=("Arial", 10), anchor='e').grid(
        row=0, column=0, padx=(10, 5), pady=5, sticky='e'
    )
    hp_percentage_entry = tk.Entry(settings_frame, width=10)
    hp_percentage_entry.insert(0, str(shared.config.get("hp_threshold", 50)))
    hp_percentage_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    tk.Label(settings_frame, text="HP Pot Key:", font=("Arial", 10), anchor='e').grid(
        row=0, column=2, padx=(10, 5), pady=5, sticky='e'
    )
    hp_pot_key_entry = tk.Entry(settings_frame, width=10)
    hp_pot_key_entry.insert(0, shared.config.get("hp_pot_key", '1'))
    hp_pot_key_entry.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

    # MP Pot Threshold and MP Pot Key row
    tk.Label(settings_frame, text="MP Pot Threshold (%):", font=("Arial", 10), anchor='e').grid(
        row=1, column=0, padx=(10, 5), pady=5, sticky='e'
    )
    mp_percentage_entry = tk.Entry(settings_frame, width=10)
    mp_percentage_entry.insert(0, str(shared.config.get("mp_threshold", 50)))
    mp_percentage_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

    tk.Label(settings_frame, text="MP Pot Key:", font=("Arial", 10), anchor='e').grid(
        row=1, column=2, padx=(10, 5), pady=5, sticky='e'
    )
    mp_pot_key_entry = tk.Entry(settings_frame, width=10)
    mp_pot_key_entry.insert(0, shared.config.get("mp_pot_key", '2'))
    mp_pot_key_entry.grid(row=1, column=3, padx=5, pady=5, sticky='ew')

    # Attack Settings Tab content
    tk.Label(attack_settings_tab, text="Attack Settings", font=("Arial", 12, "bold")).pack(pady=10)
    attack_settings_frame = tk.Frame(attack_settings_tab)
    attack_settings_frame.pack(fill="both", expand=True)

    # Configure columns
    attack_settings_frame.columnconfigure(0, weight=1)
    attack_settings_frame.columnconfigure(1, weight=1)

    # Create top frame for settings
    attack_settings_top_frame = tk.Frame(attack_settings_frame)
    attack_settings_top_frame.pack(fill='x')

    # Configure columns in attack_settings_top_frame
    attack_settings_top_frame.columnconfigure(0, weight=1)
    attack_settings_top_frame.columnconfigure(1, weight=1)

    row = 0
    enable_basic_attack_var = tk.BooleanVar()
    enable_basic_attack_checkbox = tk.Checkbutton(
        attack_settings_top_frame,
        text="Enable Basic Attack",
        variable=enable_basic_attack_var,
        command=lambda: shared.config["attack_settings"].__setitem__(
            "enable_basic_attack",
            enable_basic_attack_var.get()
        )
    )
    enable_basic_attack_var.set(shared.config["attack_settings"].get("enable_basic_attack", False))
    enable_basic_attack_checkbox.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
    row += 1

    # Basic Attack Key
    tk.Label(attack_settings_top_frame, text="Basic Attack Key:", font=("Arial", 10)).grid(
        row=row, column=0, sticky='e', padx=5, pady=4
    )
    basic_attack_key_var = tk.StringVar()
    basic_attack_key_entry = tk.Entry(
        attack_settings_top_frame,
        textvariable=basic_attack_key_var
    )
    basic_attack_key_var.set(shared.config["attack_settings"].get("basic_attack_key", ""))
    basic_attack_key_entry.grid(row=row, column=1, sticky='w', padx=5, pady=4)
    row += 1

    # Enable Auto Target checkbox
    enable_auto_target_var = tk.BooleanVar()
    enable_auto_target_checkbox = tk.Checkbutton(
        attack_settings_top_frame,
        text="Enable Auto Target",
        variable=enable_auto_target_var,
        command=lambda: shared.config["attack_settings"].__setitem__(
            "enable_auto_target",
            enable_auto_target_var.get()
        )
    )
    enable_auto_target_var.set(shared.config["attack_settings"].get("enable_auto_target", False))
    enable_auto_target_checkbox.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
    row += 1

    # Auto Target Key
    tk.Label(attack_settings_top_frame, text="Auto Target Key:", font=("Arial", 10)).grid(
        row=row, column=0, sticky='e', padx=5, pady=4
    )
    auto_target_key_var = tk.StringVar()
    auto_target_key_entry = tk.Entry(
        attack_settings_top_frame,
        textvariable=auto_target_key_var
    )
    auto_target_key_var.set(shared.config["attack_settings"].get("auto_target_key", ""))
    auto_target_key_entry.grid(row=row, column=1, sticky='w', padx=5, pady=4)
    row += 1

    # Update config on entry changes
    basic_attack_key_var.trace_add("write", lambda *args: shared.config["attack_settings"].
                                   __setitem__("basic_attack_key", basic_attack_key_var.get()))
    auto_target_key_var.trace_add("write", lambda *args: shared.config["attack_settings"].
                                  __setitem__("auto_target_key", auto_target_key_var.get()))
    enable_auto_target_var.trace_add("write", lambda *args: shared.config["attack_settings"].
                                     __setitem__("enable_auto_target", enable_auto_target_var.get()))
    enable_basic_attack_var.trace_add("write", lambda *args: shared.config["attack_settings"].
                                      __setitem__("enable_basic_attack", enable_basic_attack_var.get()))

    # Monster Name Coordinates section (coordinate selector for monster names)
    monster_coord_frame = tk.Frame(attack_settings_frame)
    monster_coord_frame.pack(fill='x', padx=5, pady=5)

    # Button for selecting coordinates, placed at the top, centered, and with a smaller width
    select_monster_coord_button = tk.Button(
        monster_coord_frame,
        text="Select Monster Name Coordinates",
        command=lambda: select_region(update_monster_name_coord),
        width=25  # Smaller width for button
    )
    select_monster_coord_button.pack(pady=5)  # Centered alignment

    # Label to display coordinates below the button
    monster_coord_label = tk.Label(
        monster_coord_frame,
        text=f"Monster Name Coordinates: {shared.config['attack_settings'].get('monster_name_coord', 'Not Selected')}",
        font=("Arial", 10),
        anchor='center',  # Left alignment of text within label
        justify='center'
    )
    monster_coord_label.pack(side='top', padx=5, pady=(5, 0), fill='x')

    def update_monster_name_coord(region: Tuple[int, int, int, int]) -> None:
        # Save the coordinate to shared.config
        shared.config["attack_settings"]["monster_name_coord"] = region
        # Update label text to show selected coordinates below
        monster_coord_label.config(text=f"Monster Name Coordinates:\n{region}")

    # Monster Whitelist Checkbox
    enable_monster_whitelist_var = tk.BooleanVar()
    enable_monster_whitelist_checkbox = tk.Checkbutton(
        attack_settings_top_frame,
        text="Enable Monster Whitelist",
        variable=enable_monster_whitelist_var,
        command=lambda: shared.config["attack_settings"].__setitem__(
            "monster_whitelist",
            enable_monster_whitelist_var.get()
        )
    )
    enable_monster_whitelist_var.set(shared.config["attack_settings"].get("monster_whitelist", False))
    enable_monster_whitelist_checkbox.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
    row += 1
    enable_monster_whitelist_var.trace_add("write", lambda *args: shared.config["attack_settings"].
                                           __setitem__("monster_whitelist", enable_monster_whitelist_var.get()))
    # Monster Names Entry Section
    tk.Label(attack_settings_frame, text="Monster Names (comma-separated):", font=("Arial", 10)).pack(pady=(10, 5))

    monster_name_var = tk.StringVar()
    monster_name_entry = tk.Entry(attack_settings_frame, textvariable=monster_name_var, width=50)
    monster_name_entry.pack(pady=(5, 10))

    # Load saved monster names if available in config
    if "monster_names" in shared.config["attack_settings"]:
        monster_name_var.set(", ".join(shared.config["attack_settings"]["monster_names"]))

    def save_monster_names() -> None:
        # Get the monster names, split by commas, and save to the config
        monster_names = [name.strip() for name in monster_name_var.get().split(',') if name.strip()]
        shared.config["attack_settings"]["monster_names"] = monster_names

    # Save the monster names on entry change
    monster_name_var.trace_add("write", lambda *args: save_monster_names())

    # Buff Settings Tab content
    def update_buff_settings() -> None:
        # Clear the current contents of buff_settings_tab
        for widget in buff_settings_tab.winfo_children():
            widget.destroy()

        # Add title label
        tk.Label(buff_settings_tab, text="Buff Settings", font=("Arial", 12, "bold")).pack(pady=10)

        # Keep track of cooldown and cast time entries
        buff_cooldown_entries = []
        buff_cast_time_entries = []

        # Get the list of buffs
        buffs = [skill for skill in shared.config["attack_settings"].get("skills", []) if skill.get("buff")]

        if not buffs:
            # Display message
            tk.Label(buff_settings_tab, text="Please select skills under Skill Settings",
                     font=("Arial", 12)).pack(pady=10)
            return

        # Add coordinate selector at the top
        coord_frame = tk.Frame(buff_settings_tab)
        coord_frame.pack(fill='x', padx=5, pady=5)

        coord_label = tk.Label(coord_frame, text="Coordinates: Not Selected", font=("Arial", 10))
        coord_label.pack(side='left', padx=5)

        def update_buff_coord(region: Tuple[int, int, int, int]) -> None:
            # Save the coordinate to shared.config
            shared.config["buff_coordinates"] = region
            coord_label.config(text=f"Coordinates: {region}")

        select_coord_button = tk.Button(coord_frame, text="Select Coordinates",
                                        command=lambda: select_region(update_buff_coord))
        select_coord_button.pack(side='left', padx=5)

        # If coordinates are already saved, display them
        if shared.config.get('buff_coordinates'):
            coord_label.config(text=f"Coordinates: {shared.config['buff_coordinates']}")

        # Add headers
        header_frame = tk.Frame(buff_settings_tab)
        header_frame.pack(fill='x', padx=0, pady=5)

        header_frame.columnconfigure(0, weight=0)  # Icon
        header_frame.columnconfigure(1, weight=0)  # Skill Name
        header_frame.columnconfigure(2, weight=0)  # Party?
        header_frame.columnconfigure(3, weight=0)  # Cooldown
        header_frame.columnconfigure(4, weight=0)  # Cast Time

        tk.Label(header_frame, text="Icon", font=("Arial", 10, "bold"), width=10).grid(row=0, column=0, padx=0)
        tk.Label(header_frame, text="Skill Name", font=("Arial", 10, "bold"), width=10).grid(row=0, column=1, padx=0)
        tk.Label(header_frame, text="Party?", font=("Arial", 10, "bold"), width=10).grid(row=0, column=2, padx=0)
        tk.Label(header_frame, text="Cooldown (s)", font=("Arial", 10, "bold"), width=10).grid(row=0, column=3, padx=0)
        tk.Label(header_frame, text="Cast Time (ms)", font=("Arial", 10, "bold"),
                 width=12).grid(row=0, column=4, padx=0)

        # For each buff, display the icon, name, and "Party?" checkbox
        for buff in buffs:
            buff_frame = tk.Frame(buff_settings_tab)
            buff_frame.pack(fill='x', padx=5, pady=5)

            # Configure buff columns
            buff_frame.columnconfigure(0, weight=0)  # Icon
            buff_frame.columnconfigure(1, weight=0)  # Skill Name
            buff_frame.columnconfigure(2, weight=0)  # Party?
            buff_frame.columnconfigure(3, weight=0)  # Cooldown
            buff_frame.columnconfigure(4, weight=0)  # Cast Time

            # Icon
            skill_icon_path = f"static/{shared.config['attack_settings']['selected_class'].
                                        lower()}_{buff['subclass'].lower()}_{buff['name'].lower()}.png"
            if os.path.exists(skill_icon_path):
                skill_image = tk.PhotoImage(file=skill_icon_path)
                skill_label = tk.Label(buff_frame, image=skill_image)
                skill_label.image = skill_image   # type: ignore[attr-defined] # Keep a reference
                skill_label.grid(row=0, column=0, padx=5)
            else:
                # Placeholder if image not found
                skill_label = tk.Label(buff_frame, text=buff['name'], font=("Arial", 10))
                skill_label.grid(row=0, column=0, padx=5)

            # Name
            tk.Label(buff_frame, text=buff['name'],
                     font=("Arial", 10), width=15).grid(row=0, column=1, padx=5, sticky='w')

            # "Party?" checkbox
            party_var = tk.BooleanVar(value=buff.get('party', False))
            party_checkbox = tk.Checkbutton(buff_frame, variable=party_var)

            def save_party_var(skill_name=buff['name'], party_var=party_var) -> None:
                # Update the skill in shared.config
                for skill in shared.config["attack_settings"].get("skills", []):
                    if skill['name'] == skill_name:
                        skill['party'] = party_var.get()
                        break

            party_var.trace_add("write", lambda *args, skill_name=buff['name'],
                                party_var=party_var: save_party_var(skill_name, party_var))
            party_checkbox.grid(row=0, column=2, padx=5)

            # Cooldown Entry
            cooldown_entry = tk.Entry(buff_frame, width=15)  # type: ignore[misc]
            cooldown_entry.grid(row=0, column=3, padx=5)

            cooldown_value = buff.get('cooldown', 0)  # Default to 0
            cooldown_entry.insert(0, str(cooldown_value))

            # Cast Time Entry
            cast_time_entry = tk.Entry(buff_frame, width=15)
            cast_time_entry.grid(row=0, column=4, padx=5)

            # Get existing Cast Time value or default to 0
            cast_time_value = buff.get('cast_time', 0)
            cast_time_entry.insert(0, str(cast_time_value))

            # Keep track of entries to update shared.config later
            buff_cooldown_entries.append((buff['name'], cooldown_entry))
            buff_cast_time_entries.append((buff['name'], cast_time_entry))

            def save_cooldown(event: tk.Event, skill_name: str = buff['name'],
                              cooldown_entry: tk.Entry = cooldown_entry) -> None:
                cooldown_text = cooldown_entry.get().strip()
                if cooldown_text == '':
                    cooldown = 0
                else:
                    try:
                        cooldown = int(cooldown_text)
                    except ValueError:
                        tk.messagebox.showerror("Error", f"Cooldown for {skill_name} must be a number.")
                        return
                # Update the skill in shared.config
                for skill in shared.config["attack_settings"].get("skills", []):
                    if skill['name'] == skill_name:
                        skill['cooldown'] = cooldown
                        break

            # Function to save Cast Time
            def save_cast_time(event: tk.Event, skill_name: str = buff['name'],
                               cast_time_entry: tk.Entry = cast_time_entry) -> None:
                cast_time_text = cast_time_entry.get().strip()
                if cast_time_text == '':
                    cast_time = 0
                else:
                    try:
                        cast_time = int(cast_time_text)
                    except ValueError:
                        tk.messagebox.showerror("Error", f"Cast Time for {skill_name} must be a number.")
                        return
                # Update the skill in shared.config
                for skill in shared.config["attack_settings"].get("skills", []):
                    if skill['name'] == skill_name:
                        skill['cast_time'] = cast_time
                        break

            cooldown_entry.bind("<FocusOut>", save_cooldown)
            cast_time_entry.bind("<FocusOut>", save_cast_time)

    # Heal Settings Tab content
    def update_heal_settings() -> None:
        # Clear the current contents of heal_settings_tab
        for widget in heal_settings_tab.winfo_children():
            widget.destroy()

        # Add title label
        tk.Label(heal_settings_tab, text="Heal Settings", font=("Arial", 12, "bold")).pack(pady=10)

        # Heal Threshold Entry at the top of the Heal Settings tab
        threshold_frame = tk.Frame(heal_settings_tab)
        threshold_frame.pack(fill='x', padx=10, pady=10)

        # Label for Heal Threshold
        tk.Label(threshold_frame, text="Heal Threshold (%):", font=("Arial", 10), anchor='e').grid(
            row=0, column=0, padx=(10, 5), pady=5, sticky='e'
        )

        # Entry for Heal Threshold
        heal_threshold_entry = tk.Entry(threshold_frame, width=10)
        heal_threshold_entry.insert(0, str(shared.config.get("heal_threshold", 50)))
        heal_threshold_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        def save_heal_threshold(event: tk.Event) -> None:
            threshold_text = heal_threshold_entry.get().strip()
            if threshold_text == '':
                heal_threshold = 0  # Default to 0 if empty
            else:
                try:
                    heal_threshold = int(threshold_text)
                except ValueError:
                    tk.messagebox.showerror("Error", "Heal Threshold must be a valid number.")
                    return
            shared.config["heal_threshold"] = heal_threshold

        # Keep track of cooldown and cast time entries
        heal_cooldown_entries = []
        heal_cast_time_entries = []

        # Get the list of heals
        heals = [skill for skill in shared.config["attack_settings"].get("skills", []) if skill.get("heal")]

        if not heals:
            # Display message
            tk.Label(heal_settings_tab, text="Please select skills under Skill Settings",
                     font=("Arial", 12)).pack(pady=10)
            return

        # Add headers
        header_frame = tk.Frame(heal_settings_tab)
        header_frame.pack(fill='x', padx=0, pady=5)

        header_frame.columnconfigure(0, weight=0)  # Icon
        header_frame.columnconfigure(1, weight=0)  # Skill Name
        header_frame.columnconfigure(2, weight=0)  # Party?
        header_frame.columnconfigure(3, weight=0)  # Cooldown
        header_frame.columnconfigure(4, weight=0)  # Cast Time

        tk.Label(header_frame, text="Icon", font=("Arial", 10, "bold"), width=10).grid(row=0, column=0, padx=0)
        tk.Label(header_frame, text="Skill Name", font=("Arial", 10, "bold"), width=10).grid(row=0, column=1, padx=0)
        tk.Label(header_frame, text="Party?", font=("Arial", 10, "bold"), width=10).grid(row=0, column=2, padx=0)
        tk.Label(header_frame, text="Cooldown (s)", font=("Arial", 10, "bold"), width=10).grid(row=0, column=3, padx=0)
        tk.Label(header_frame, text="Cast Time (ms)",
                 font=("Arial", 10, "bold"), width=12).grid(row=0, column=4, padx=0)
        
        # For each heal, display the icon, name, "Party?" checkbox
        for heal in heals:
            heal_frame = tk.Frame(heal_settings_tab)
            heal_frame.pack(fill='x', padx=5, pady=5)
            # Configure heal columns
            heal_frame.columnconfigure(0, weight=0)  # Icon
            heal_frame.columnconfigure(1, weight=0)  # Skill Name
            heal_frame.columnconfigure(2, weight=0)  # Party?
            heal_frame.columnconfigure(3, weight=0)  # Cooldown
            heal_frame.columnconfigure(4, weight=0)  # Cast Time

            # Icon
            skill_icon_path = f"static/{shared.config['attack_settings']['selected_class']
                                        .lower()}_{heal['subclass'].lower()}_{heal['name'].lower()}.png"
            if os.path.exists(skill_icon_path):
                skill_image = tk.PhotoImage(file=skill_icon_path)
                skill_label = tk.Label(heal_frame, image=skill_image)
                skill_label.image = skill_image  # type: ignore[attr-defined] # Keep a reference
                skill_label.grid(row=0, column=0, padx=5)
            else:
                # Placeholder if image not found
                skill_label = tk.Label(heal_frame, text=heal['name'], font=("Arial", 10))
                skill_label.pack(side='left', padx=5)

            # Name
            tk.Label(heal_frame, text=heal['name'],
                     font=("Arial", 10), width=15).grid(row=0, column=1, padx=5, sticky='w')

            # "Party?" checkbox
            party_var = tk.BooleanVar(value=heal.get('party', False))
            party_checkbox = tk.Checkbutton(heal_frame, text='Party?', variable=party_var)

            def save_party_var(skill_name=heal['name'], party_var=party_var) -> None:
                # Update the skill in shared.config
                for skill in shared.config["attack_settings"].get("skills", []):
                    if skill['name'] == skill_name:
                        skill['party'] = party_var.get()
                        break

            party_var.trace_add("write", lambda *args, skill_name=heal['name'],
                                party_var=party_var: save_party_var(skill_name, party_var))
            party_checkbox.grid(row=0, column=2, padx=5)

            # Cooldown Entry
            cooldown_entry = tk.Entry(heal_frame, width=15)  # type: ignore[misc]
            cooldown_entry.grid(row=0, column=3, padx=5)

            cooldown_value = heal.get('cooldown', 0)  # Default to 0
            cooldown_entry.insert(0, str(cooldown_value))

            # Cast Time Entry
            cast_time_entry = tk.Entry(heal_frame, width=15)
            cast_time_entry.grid(row=0, column=4, padx=5)

            # Get existing Cast Time value or default to 0
            cast_time_value = heal.get('cast_time', 0)
            cast_time_entry.insert(0, str(cast_time_value))

            # Keep track of entries to update shared.config later
            heal_cooldown_entries.append((heal['name'], cooldown_entry))
            heal_cast_time_entries.append((heal['name'], cast_time_entry))

            def save_cooldown(event: tk.Event, skill_name: str = heal['name'],
                              cooldown_entry: tk.Entry = cooldown_entry) -> None:
                cooldown_text = cooldown_entry.get().strip()
                if cooldown_text == '':
                    cooldown = 0
                else:
                    try:
                        cooldown = int(cooldown_text)
                    except ValueError:
                        tk.messagebox.showerror("Error", f"Cooldown for {skill_name} must be a number.")
                        return
                # Update the skill in shared.config
                for skill in shared.config["attack_settings"].get("skills", []):
                    if skill['name'] == skill_name:
                        skill['cooldown'] = cooldown
                        break

            # Function to save Cast Time
            def save_cast_time(event: tk.Event, skill_name: str = heal['name'],
                               cast_time_entry: tk.Entry = cast_time_entry) -> None:
                cast_time_text = cast_time_entry.get().strip()
                if cast_time_text == '':
                    cast_time = 0
                else:
                    try:
                        cast_time = int(cast_time_text)
                    except ValueError:
                        tk.messagebox.showerror("Error", f"Cast Time for {skill_name} must be a number.")
                        return
                # Update the skill in shared.config
                for skill in shared.config["attack_settings"].get("skills", []):
                    if skill['name'] == skill_name:
                        skill['cast_time'] = cast_time
                        break

            heal_threshold_entry.bind("<FocusOut>", save_heal_threshold)
            cooldown_entry.bind("<FocusOut>", save_cooldown)
            cast_time_entry.bind("<FocusOut>", save_cast_time)

    # Skill Settings Tab
    tk.Label(skill_settings_tab, text="Skill Settings", font=("Arial", 12, "bold")).pack(pady=10)

    # Top frame for Enable Basic Attack and Select Class
    skill_settings_top_frame = tk.Frame(skill_settings_tab)
    skill_settings_top_frame.pack(fill='x')

    # Configure columns in attack_settings_top_frame
    skill_settings_top_frame.columnconfigure(0, weight=1)
    skill_settings_top_frame.columnconfigure(1, weight=1)

    row = 0

    # Create a frame to hold 'Select Class' label and combobox
    select_class_frame = tk.Frame(skill_settings_top_frame)
    select_class_frame.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=5, pady=4)

    # Configure columns in select_class_frame
    select_class_frame.columnconfigure(0, weight=1)
    select_class_frame.columnconfigure(1, weight=1)

    tk.Label(select_class_frame, text="Select Class:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, sticky='e', padx=5, pady=4
    )
    selected_class = tk.StringVar()

    shared.config["class_options"] = list(skill_data.keys())

    selected_class.set(
        shared.config["attack_settings"].get(
            "selected_class",
            shared.config["class_options"][0] if shared.config["class_options"] else ''
        )
    )

    # Create Combobox
    class_dropdown = ttk.Combobox(
        select_class_frame,
        textvariable=selected_class,
        values=shared.config["class_options"]
    )
    class_dropdown.grid(row=0, column=1, sticky='w', padx=5, pady=4)
    row += 1

    # Scrollable frame for skill tree
    scrollable_skill_settings_frame = add_scrollable_frame(skill_settings_tab)

    # Configure columns
    scrollable_skill_settings_frame.columnconfigure(0, weight=1)
    scrollable_skill_settings_frame.columnconfigure(1, weight=1)

    # Skill tree frame with notebook
    subclass_notebook = ttk.Notebook(scrollable_skill_settings_frame)
    subclass_notebook.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
    scrollable_skill_settings_frame.rowconfigure(0, weight=1)
    scrollable_skill_settings_frame.columnconfigure(1, weight=1)

    def update_subclasses(*args) -> None:
        # Clean Old Widgets
        for tab_id in subclass_notebook.tabs():
            subclass_notebook.forget(tab_id)

        selected = selected_class.get()
        logger.debug(f"Selected class: {selected}")

        if not selected or selected == 'None':
            logger.warning("No class selected in update_subclasses.")
            return
        if selected not in skill_data:
            logger.warning(f"Selected class '{selected}' not found in skill_data.")
            return

        # Update subclasses
        shared.config["attack_settings"]["selected_class"] = selected

        for subclass in skill_data[selected]:
            logger.debug(f"Loading subclass: {subclass}")
            subclass_tab = ttk.Frame(subclass_notebook)
            subclass_notebook.add(subclass_tab, text=subclass)

            skills = skill_data[selected][subclass]

            # Skill selection
            skill_row = 0

            # Add column headers
            header_frame = tk.Frame(subclass_tab)
            header_frame.grid(row=skill_row, column=0, sticky='nsew', padx=5, pady=2)
            skill_row += 1

            # Configure columns with spacers
            header_frame.columnconfigure(0, weight=0)  # Checkbox
            header_frame.columnconfigure(1, weight=0)  # Icon
            header_frame.columnconfigure(2, weight=1)  # Skill Name
            header_frame.columnconfigure(3, weight=0)  # Spacer
            header_frame.columnconfigure(4, weight=0)  # Skill Bar
            header_frame.columnconfigure(5, weight=0)  # Spacer
            header_frame.columnconfigure(6, weight=0)  # Slot
            header_frame.columnconfigure(7, weight=0)  # Buff?
            header_frame.columnconfigure(8, weight=0)  # Heal?

            # Column headers
            tk.Label(header_frame, text="Activate", font=("Arial", 10)).grid(row=0, column=0, padx=1)  # For checkbox
            tk.Label(header_frame, text="", font=("Arial", 10)).grid(row=0, column=1, padx=1)  # For icon
            tk.Label(header_frame, text="Skill Name", font=("Arial", 10)).grid(row=0, column=2, padx=10)
            tk.Label(header_frame, text="", font=("Arial", 10)).grid(row=0, column=3, padx=30)  # Spacer
            tk.Label(header_frame, text="Skill Bar", font=("Arial", 10)).grid(row=0, column=4, padx=1)
            tk.Label(header_frame, text="Skill Slot", font=("Arial", 10)).grid(row=0, column=6, padx=1)
            tk.Label(header_frame, text="Buff?", font=("Arial", 10)).grid(row=0, column=7, padx=1)
            tk.Label(header_frame, text="Heal?", font=("Arial", 10)).grid(row=0, column=8, padx=1)

            for skill_name in skills:
                skill_frame = tk.Frame(subclass_tab)
                skill_frame.grid(row=skill_row, column=0, sticky='nsew', padx=5, pady=2)
                skill_row += 1

                # Configure columns with spacers
                skill_frame.columnconfigure(0, weight=0)  # Checkbox
                skill_frame.columnconfigure(1, weight=0)  # Icon
                skill_frame.columnconfigure(2, weight=1)  # Skill Name
                skill_frame.columnconfigure(3, weight=0)  # Spacer
                skill_frame.columnconfigure(4, weight=0)  # Skill Bar Entry
                skill_frame.columnconfigure(5, weight=0)  # Spacer
                skill_frame.columnconfigure(6, weight=0)  # Slot Entry
                skill_frame.columnconfigure(7, weight=0)  # Buff Checkbox
                skill_frame.columnconfigure(8, weight=0)  # Heal Checkbox

                skill_var = tk.BooleanVar()
                skill_checkbox = tk.Checkbutton(skill_frame, variable=skill_var)
                skill_checkbox.grid(row=0, column=0, sticky='nsew')

                # Skill icon (assuming icons are stored in 'static' folder)
                skill_icon_path = f"static/{selected.lower()}_{subclass.lower()}_{skill_name.lower()}.png"
                if os.path.exists(skill_icon_path):
                    skill_image = tk.PhotoImage(file=skill_icon_path)
                    skill_label = tk.Label(skill_frame, image=skill_image)
                    skill_label.image = skill_image  # type: ignore[attr-defined] # Keep a reference
                    skill_label.grid(row=0, column=1, padx=5, sticky='w')  # Use grid() instead of pack()
                else:
                    # Placeholder if image not found
                    skill_label = tk.Label(skill_frame, text=skill_name, font=("Arial", 10))
                    skill_label.grid(row=0, column=1, padx=5, sticky='w')

                # Skill name
                tk.Label(skill_frame, text=skill_name, font=("Arial", 10)).grid(row=0, column=2, padx=7, sticky='w')

                # Spacer between Skill Name and Skill Bar
                tk.Label(skill_frame, text="", font=("Arial", 10)).grid(row=0, column=3, padx=10)

                # Skill bar entry (without label)
                skill_bar_entry = tk.Entry(skill_frame, width=5)
                skill_bar_entry.grid(row=0, column=4, padx=5)

                # Spacer between Skill Bar and Slot
                tk.Label(skill_frame, text="", font=("Arial", 10)).grid(row=0, column=5, padx=10)

                # Slot number entry (without label)
                slot_entry = tk.Entry(skill_frame, width=5)
                slot_entry.grid(row=0, column=6, padx=5)

                # Buff? Checkbox
                buff_var = tk.BooleanVar()
                buff_checkbox = tk.Checkbutton(skill_frame, variable=buff_var)
                buff_checkbox.grid(row=0, column=7, padx=5)

                # Heal? Checkbox
                heal_var = tk.BooleanVar()
                heal_checkbox = tk.Checkbutton(skill_frame, variable=heal_var)
                heal_checkbox.grid(row=0, column=8, padx=5)

                # Load saved skill settings if available
                saved_skill = next(
                    (s for s in shared.config["attack_settings"].get("skills", []) if s["name"] == skill_name),
                    None
                )
                if saved_skill:
                    logger.debug(f"Loading saved skill: {saved_skill}")
                    skill_var.set(saved_skill["enabled"])
                    skill_bar_entry.insert(0, saved_skill["skill_bar"])
                    slot_entry.insert(0, saved_skill["slot"])
                    buff_var.set(saved_skill.get("buff", False))
                    heal_var.set(saved_skill.get("heal", False))

                # Save skill settings
                def save_skill(skill_name=skill_name, subclass=subclass, skill_var=skill_var,
                               skill_bar_entry=skill_bar_entry, slot_entry=slot_entry,
                               buff_var=buff_var, heal_var=heal_var) -> None:
                    skill_info = {
                        "name": skill_name,
                        "subclass": subclass,
                        "enabled": skill_var.get(),
                        "skill_bar": skill_bar_entry.get(),
                        "slot": slot_entry.get(),
                        "buff": buff_var.get(),
                        "heal": heal_var.get()
                    }
                    # Remove any existing entry with this skill name
                    shared.config["attack_settings"]["skills"] = [
                        s for s in shared.config["attack_settings"].get("skills", [])
                        if s["name"] != skill_name
                    ]
                    # Add the updated skill info
                    shared.config["attack_settings"]["skills"].append(skill_info)
                    update_buff_settings()
                    update_heal_settings()
                # Bind save on change and update settings

                skill_var.trace_add("write", lambda *args, save_skill=save_skill: save_skill())  # type: ignore[misc]
                heal_var.trace_add("write", lambda *args, save_skill=save_skill: save_skill())  # type: ignore[misc]
                buff_var.trace_add("write", lambda *args, save_skill=save_skill: save_skill())  # type: ignore[misc]
                skill_bar_entry.bind("<FocusOut>", lambda e, save_skill=save_skill: save_skill())  # type: ignore[misc]
                slot_entry.bind("<FocusOut>", lambda e, save_skill=save_skill: save_skill())  # type: ignore[misc]

        update_buff_settings()
        update_heal_settings()

    selected_class.trace_add("write", update_subclasses)
    update_subclasses()

    def save_settings() -> None:
        try:
            shared.config["hp_threshold"] = int(hp_percentage_entry.get())
            shared.config["mp_threshold"] = int(mp_percentage_entry.get())
            shared.config["hp_pot_key"] = hp_pot_key_entry.get()
            shared.config["mp_pot_key"] = mp_pot_key_entry.get()
            shared.config["window_name"] = window_name_entry.get()
            shared.config["attack_settings"]["enable_basic_attack"] = enable_basic_attack_var.get()
            write_config_to_file(shared.config)
            tk.messagebox.showinfo("Settings", "Settings saved successfully.")
            logger.info("Settings Saved Successfully")
        except ValueError:
            tk.messagebox.showerror("Error", "Threshold values must be numeric.")
            logger.error("Settings Not Saved Threshold values must be numeric.")
        except Exception as e:
            logger.error(f"Failed to save config settings: {e}")

    config_frame = tk.Frame(window)
    config_frame.pack(pady=5)

    save_all_settings_button = tk.Button(config_frame, text="Save Settings", command=save_settings)
    save_all_settings_button.pack(pady=10)

    window.mainloop()


def find_window(window_title: str) -> Optional[Any]:
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        return windows[0]
    else:
        logger.warning(f"Window named {window_title} not found!")
        return None


class RegionSelector:

    def __init__(self, root: tk.Toplevel, callback: Callable[[Tuple[int, int, int, int]], None]) -> None:
        self.root = root
        self.callback = callback
        self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.start_x: Optional[int] = None
        self.start_y: Optional[int] = None
        self.rect_id: Optional[int] = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event: tk.Event) -> None:
        self.start_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        self.start_y = self.root.winfo_pointery() - self.root.winfo_rooty()
        if self.rect_id:
            self.canvas.delete(self.rect_id)

    def on_mouse_drag(self, event: tk.Event) -> None:
        cur_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        cur_y = self.root.winfo_pointery() - self.root.winfo_rooty()
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        if self.start_x is not None and self.start_y is not None:
            self.rect_id = self.canvas.create_rectangle(
                self.start_x,
                self.start_y,
                cur_x,
                cur_y,
                outline='red', width=2
            )

    def on_button_release(self, event: tk.Event) -> None:
        end_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        end_y = self.root.winfo_pointery() - self.root.winfo_rooty()
        if self.start_x is not None and self.start_y is not None:
            selected_region = (
                min(self.start_x, end_x), min(self.start_y, end_y),
                max(self.start_x, end_x), max(self.start_y, end_y)
            )
            logger.info(f"Selected Region: {selected_region}")  # Debugging the selected region
            self.callback(selected_region)
        self.root.destroy()

    def get_region(self) -> None:
        self.root.mainloop()


def select_region(callback: Callable[[Tuple[int, int, int, int]], None]) -> None:
    region_window = tk.Toplevel()
    region_window.attributes("-fullscreen", True)
    region_window.attributes("-alpha", 0.3)  # Make the screen semi-transparent
    region_window.lift()
    region_window.attributes("-topmost", True)
    selector = RegionSelector(region_window, callback)
    selector.get_region()


def add_scrollable_frame(tab: ttk.Frame) -> ttk.Frame:
    # Create a canvas for adding scrollable content
    canvas = tk.Canvas(tab)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a vertical scrollbar linked to the canvas
    scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a frame inside the canvas to hold the actual content
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

    # Configure the canvas to work with the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Update the scrollregion and frame width when the frame or canvas size changes
    def on_frame_configure(event: tk.Event) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(scrollable_frame_id, width=canvas.winfo_width())

    scrollable_frame.bind("<Configure>", on_frame_configure)

    def on_canvas_configure(event: tk.Event) -> None:
        canvas.itemconfig(scrollable_frame_id, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    # Function to handle mouse wheel scrolling
    def _on_mousewheel(event: tk.Event) -> None:
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")
        elif event.num == 4:
            canvas.yview_scroll(-1, "units")

    # Bind mouse wheel events when mouse is over the canvas
    scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    scrollable_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # For Linux (scroll wheel events)
    scrollable_frame.bind("<Button-4>", _on_mousewheel)
    scrollable_frame.bind("<Button-5>", _on_mousewheel)

    return scrollable_frame
