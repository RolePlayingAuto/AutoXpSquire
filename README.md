# AutoXpSquire

Helper for your RPG fantasies to become the best Knight via Python

## Setup

- Run `pip install -r requirements.txt`

- Run the script via admin cmd or powershell  `python main.py`

## Usage
- Save Settings if you want any changes to be loaded in next start.

### Control 
- Set the `Game Window Name` for the target game you want to run
- `Start Auto-Attack` and `Enable HP/MP Check` can be ticked to be enabled when bot starts.
- `Start Bot` starts the bot.
- Stop bot via Alt-Tab `Stop Bot` button.
- Alternatively use `F11` to start and `ESC` to stop.

### Settings
- Select the HP and MP bar regions.
- Enter auto pot thresholds and pot keys.

### Attack Settings
- Enable R auto attack if you want it in.
- Classes and skills will be loaded from the `config/skill_data.yml` file. Enter any type of class skills and skills types in the file following example format to show your classes and skills here. Skill images can optionally be stored in `static/` folder to see them in GUI. Image names should follow `{class_name}_{skill_type}_{skill_name}` format.
- Tick the skills you want to be used, enter their skill bar shortcuts and skill slot shortcuts. Example Skill bar `F4` Slot `5`.
