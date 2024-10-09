import json
import os
import time
import tkinter as tk
from tkinter import messagebox, ttk  # noqa: F401
from typing import Any, Callable, Optional, Tuple

import pygetwindow as gw

import utils.shared as shared
from utils.auto_attack import start_auto_attack, stop_auto_attack
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
    window.geometry("700x800")  # Adjusted for better initial size
    tab_control = ttk.Notebook(window)
    control_tab = ttk.Frame(tab_control)
    settings_tab = ttk.Frame(tab_control)
    attack_settings_tab = ttk.Frame(tab_control)
    tab_control.add(control_tab, text="Control")
    tab_control.add(settings_tab, text="Settings")
    tab_control.add(attack_settings_tab, text="Attack Settings")
    tab_control.pack(expand=1, fill="both")

    # Control Tab
    tk.Label(control_tab, text="AutoXpSquire Bot Control", font=("Arial", 14)).pack(pady=10)
    tk.Label(control_tab, text="Game Window Name:").pack()
    window_name_entry = tk.Entry(control_tab)
    window_name_entry.pack()
    window_name_entry.insert(0, shared.config.get('window_name', ''))

    # Auto-attack checkbox
    attack_var = tk.BooleanVar()
    attack_checkbox = tk.Checkbutton(control_tab, text="Start Auto-Attack", variable=attack_var,
                                     command=lambda: config_variable_setter(shared.config, attack_var.get(),
                                                                            "auto_attack_toggle"))
    attack_var.set(shared.config.get("auto_attack_toggle", False))
    attack_checkbox.pack()

    # HP and MP check checkbox
    hp_mp_check_var = tk.BooleanVar()
    hp_mp_checkbox = tk.Checkbutton(control_tab, text="Enable HP/MP Check", variable=hp_mp_check_var,
                                    command=lambda: config_variable_setter(shared.config, hp_mp_check_var.get(),
                                                                           "hp_mp_check"))
    hp_mp_check_var.set(shared.config.get("hp_mp_check", False))
    hp_mp_checkbox.pack()

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
        time.sleep(0.5)
        if attack_var.get():
            shared.auto_attack_thread = start_auto_attack(shared.config)
        if hp_mp_check_var.get():
            shared.hp_mp_check_thread = start_hp_mp_check(shared.config)
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
        logger.info("Bot stopped")

    start_button = tk.Button(control_tab, text="Start Bot", command=start_bot)
    start_button.pack(pady=5)

    stop_button = tk.Button(control_tab, text="Stop Bot", command=stop_bot)
    stop_button.pack(pady=5)

    # Settings Tab with sub-tabs
    settings_notebook = ttk.Notebook(settings_tab)
    settings_notebook.pack(expand=1, fill="both")

    hp_mp_tab = ttk.Frame(settings_notebook)
    other_settings_tab = ttk.Frame(settings_notebook)
    settings_notebook.add(hp_mp_tab, text="HP/MP")
    settings_notebook.add(other_settings_tab, text="Other Settings")

    # HP/MP Tab content
    tk.Label(hp_mp_tab, text="HP/MP Settings", font=("Arial", 12)).pack(pady=10)

    # HP and MP bar selection buttons
    set_hp_button = tk.Button(hp_mp_tab, text="Select HP Bar Region",
                              command=lambda: select_region(update_hp_bar_position))
    set_hp_button.pack(pady=5)

    set_mp_button = tk.Button(hp_mp_tab, text="Select MP Bar Region",
                              command=lambda: select_region(update_mp_bar_position))
    set_mp_button.pack(pady=5)

    # Labels to display the coordinates
    hp_coord_label = tk.Label(hp_mp_tab, text="HP Bar Coordinates: Not Selected")
    hp_coord_label.pack(pady=5)

    mp_coord_label = tk.Label(hp_mp_tab, text="MP Bar Coordinates: Not Selected")
    mp_coord_label.pack(pady=5)

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
    settings_frame = tk.Frame(hp_mp_tab)
    settings_frame.pack(pady=10)

    tk.Label(settings_frame, text="HP Pot Threshold (%):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
    hp_percentage_entry = tk.Entry(settings_frame, width=5)
    hp_percentage_entry.insert(0, str(shared.config.get("hp_threshold", 50)))
    hp_percentage_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(settings_frame, text="HP Pot Key:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
    hp_pot_key_entry = tk.Entry(settings_frame, width=5)
    hp_pot_key_entry.insert(0, shared.config.get("hp_pot_key", '1'))
    hp_pot_key_entry.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(settings_frame, text="MP Pot Threshold (%):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
    mp_percentage_entry = tk.Entry(settings_frame, width=5)
    mp_percentage_entry.insert(0, str(shared.config.get("mp_threshold", 50)))
    mp_percentage_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(settings_frame, text="MP Pot Key:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
    mp_pot_key_entry = tk.Entry(settings_frame, width=5)
    mp_pot_key_entry.insert(0, shared.config.get("mp_pot_key", '2'))
    mp_pot_key_entry.grid(row=1, column=3, padx=5, pady=5)
    # Attack Settings Tab
    tk.Label(attack_settings_tab, text="Attack Settings", font=("Arial", 12)).pack(pady=10)

    # Enable R Attack checkbox
    enable_basic_attack_var = tk.BooleanVar()
    enable_basic_attack_checkbox = tk.Checkbutton(attack_settings_tab, text="Enable R Attack",
                                                  variable=enable_basic_attack_var)
    enable_basic_attack_var.set(shared.config["attack_settings"].get("enable_basic_attack", False))
    enable_basic_attack_checkbox.pack()

    # Class selection dropdown
    tk.Label(attack_settings_tab, text="Select Class:").pack(pady=4)
    selected_class = tk.StringVar()

    selected_class.set(shared.config["attack_settings"].get("selected_class",
                                                            shared.config["class_options"][0]
                                                            if shared.config["class_options"] else ''))
    shared.config["class_options"] = list(skill_data.keys())

    # Create Combobox
    class_dropdown = ttk.Combobox(attack_settings_tab,
                                  textvariable=selected_class, values=shared.config["class_options"])
    class_dropdown.pack()

    # Skill tree frame with canvas and scrollbar
    subclass_notebook = ttk.Notebook(attack_settings_tab)
    subclass_notebook.pack(expand=1, fill="both")

    def update_subclasses(*args) -> None:
        # Clean Old Widgets
        for tab in subclass_notebook.tabs():
            subclass_notebook.forget(tab)

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
            for skill_name in skills:
                skill_frame = tk.Frame(subclass_tab)
                skill_frame.pack(fill=tk.X, padx=5, pady=2)

                skill_var = tk.BooleanVar()
                skill_checkbox = tk.Checkbutton(skill_frame, variable=skill_var)
                skill_checkbox.pack(side=tk.LEFT)

                # Skill icon (assuming icons are stored in 'static' folder)
                skill_icon_path = f"static/{selected.lower()}_{subclass.lower()}_{skill_name.lower()}.png"
                if os.path.exists(skill_icon_path):
                    skill_image = tk.PhotoImage(file=skill_icon_path)
                    skill_label = tk.Label(skill_frame, image=skill_image)
                    skill_label.image = skill_image  # type: ignore[attr-defined] # for keeping reference
                    skill_label.pack(side=tk.LEFT, padx=5)
                else:
                    # Resim bulunamadığında placeholder
                    skill_label = tk.Label(skill_frame, text=skill_name)
                    skill_label.pack(side=tk.LEFT, padx=5)

                # Skill name
                tk.Label(skill_frame, text=skill_name).pack(side=tk.LEFT, padx=5)

                # Skill bar entry
                tk.Label(skill_frame, text="Skill Bar:").pack(side=tk.LEFT, padx=5)
                skill_bar_entry = tk.Entry(skill_frame, width=3)
                skill_bar_entry.pack(side=tk.LEFT, padx=5)

                # Slot number entry
                tk.Label(skill_frame, text="Slot:").pack(side=tk.LEFT, padx=5)
                slot_entry = tk.Entry(skill_frame, width=3)
                slot_entry.pack(side=tk.LEFT, padx=5)

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

                # Save skill settings
                def save_skill(skill_name=skill_name, subclass=subclass, skill_var=skill_var,
                               skill_bar_entry=skill_bar_entry, slot_entry=slot_entry) -> None:
                    skill_info = {
                        "name": skill_name,
                        "subclass": subclass,
                        "enabled": skill_var.get(),
                        "skill_bar": skill_bar_entry.get(),
                        "slot": slot_entry.get()
                    }
                    # Remove any existing entry with this skill name
                    shared.config["attack_settings"]["skills"] = [
                        s for s in shared.config["attack_settings"]["skills"]
                        if s["name"] != skill_name
                    ]
                    # Add the updated skill info
                    shared.config["attack_settings"]["skills"].append(skill_info)

                # Bind save on change
                skill_var.trace_add("write", lambda *args, save_skill=save_skill: save_skill())  # type: ignore[misc]
                skill_bar_entry.bind("<FocusOut>", lambda e, save_skill=save_skill: save_skill())  # type: ignore[misc]
                slot_entry.bind("<FocusOut>", lambda e, save_skill=save_skill: save_skill())  # type: ignore[misc]

    selected_class.trace_add("write", update_subclasses)
    update_subclasses()

    # Configuration save/load buttons
    def load_configuration() -> None:
        if os.path.exists("config/config.json"):
            with open("config/config.json", "r") as f:
                json_config = json.load(f)
                # Update only the keys that are present in json_config
                for key in json_config:
                    shared.config[key] = json_config[key]

            # Update GUI elements based on the keys present in config
            if 'hp_threshold' in shared.config:
                hp_percentage_entry.delete(0, tk.END)
                hp_percentage_entry.insert(0, str(shared.config['hp_threshold']))
            if 'mp_threshold' in shared.config:
                mp_percentage_entry.delete(0, tk.END)
                mp_percentage_entry.insert(0, str(shared.config['mp_threshold']))
            if 'hp_pot_key' in shared.config:
                hp_pot_key_entry.delete(0, tk.END)
                hp_pot_key_entry.insert(0, shared.config['hp_pot_key'])
            if 'mp_pot_key' in shared.config:
                mp_pot_key_entry.delete(0, tk.END)
                mp_pot_key_entry.insert(0, shared.config['mp_pot_key'])
            if 'window_name' in shared.config:
                window_name_entry.delete(0, tk.END)
                window_name_entry.insert(0, shared.config['window_name'])
            if 'hp_bar_position' in shared.config:
                hp_coord_label.config(text=f"HP Bar Coordinates: {shared.config['hp_bar_position']}")
            if 'mp_bar_position' in shared.config:
                mp_coord_label.config(text=f"MP Bar Coordinates: {shared.config['mp_bar_position']}")

            if 'attack_settings' in shared.config:
                if 'enable_basic_attack' in shared.config['attack_settings']:
                    enable_basic_attack_var.set(shared.config['attack_settings']['enable_basic_attack'])
                if 'selected_class' in shared.config['attack_settings']:
                    selected_class_value = shared.config['attack_settings']['selected_class']
                    # Ensure selected_class_value is not None
                    if selected_class_value is not None:
                        selected_class.set(selected_class_value)
                    else:
                        selected_class.set('')  # Set to empty string if None
                    # Call update_subclasses to rebuild the skill tree with the saved skills
                    update_subclasses()
                else:
                    # If 'selected_class' is not in config, reset the skill tree
                    selected_class.set('')
            else:
                # If 'attack_settings' is not in config, reset relevant GUI elements
                enable_basic_attack_var.set(False)
                selected_class.set('')

            tk.messagebox.showinfo("Settings", "Configuration loaded successfully.")
        else:
            tk.messagebox.showwarning("Settings", "No configuration file found.")

    def save_configuration() -> None:
        try:
            shared.config["hp_threshold"] = int(hp_percentage_entry.get())
            shared.config["mp_threshold"] = int(mp_percentage_entry.get())
            shared.config["hp_pot_key"] = hp_pot_key_entry.get()
            shared.config["mp_pot_key"] = mp_pot_key_entry.get()
            shared.config["window_name"] = window_name_entry.get()
        except ValueError:
            tk.messagebox.showerror("Error", "Threshold values must be numeric.")
            return

        shared.config["attack_settings"]["enable_basic_attack"] = enable_basic_attack_var.get()

        write_config_to_file(shared.config)
        tk.messagebox.showinfo("Settings", "Configuration saved successfully.")

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

    save_config_button = tk.Button(config_frame, text="Save Configuration", command=save_configuration)
    save_config_button.pack(side=tk.LEFT, padx=5)

    load_config_button = tk.Button(config_frame, text="Load Configuration", command=load_configuration)
    load_config_button.pack(side=tk.LEFT, padx=5)

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
            self.rect_id = self.canvas.create_rectangle(self.start_x,
                                                        self.start_y,
                                                        cur_x,
                                                        cur_y,
                                                        outline='red', width=2)

    def on_button_release(self, event: tk.Event) -> None:
        end_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        end_y = self.root.winfo_pointery() - self.root.winfo_rooty()
        if self.start_x is not None and self.start_y is not None:
            selected_region = (min(self.start_x, end_x), min(self.start_y, end_y),
                               max(self.start_x, end_x), max(self.start_y, end_y))
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
