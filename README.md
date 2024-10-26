# AutoXpSquire

Helper for your RPG fantasies to become the best Knight via Python

## Setup

- Run `pip install -r requirements.txt`

- Run the script via admin cmd or powershell  `python main.py`

## Usage
- Save Settings if you want any changes to be loaded in next start.

### Control 
- Set the `Game Window Name` for the target game you want to run
- `Start Auto-Attack` and `Enable HP/MP Check` and `Enable Auto Buff` can be ticked to be enabled when bot starts.
- `Start Bot` starts the bot.
- Stop bot via Alt-Tab `Stop Bot` button.
- Alternatively use `F11` to start and `ESC` to stop.

### Settings
- Select the HP and MP bar regions.
- Enter auto pot thresholds and pot keys.

### Attack Settings
- Enable basic auto attack and auto targeting if you want it in. Enter the target or basic attack key in lower case. Basic attack key is pressed before every skill.
- Classes and skills will be loaded from the `config/skill_data.yml` file. Enter any type of class skills and skills types in the file following example format to show your classes and skills here. Skill images can optionally be stored in `static/` folder to see them in GUI. Image names should follow `{class_name}_{skill_type}_{skill_name}` format.
- Tick the skills you want to be used, enter their skill bar shortcuts and skill slot shortcuts. Example Skill bar `F4` Slot `5`.

### Buff Settings
- For any buff skill to be recognized and cast, their template image needs to be in `static/` with correct naming.
- From the `Skill Settings` Tab tick the `buff` for any skill that you want registered as a buff. This will add the skill to `Buff Settings` Tab under `Settings` Tab.
- Tick the `Activate` for the buff that you want it to be checked for and cast.
- Under Settings -> Buff Settings click `Select Coordinates` and select the area you want the program to search for the buff icon. This is for you to select a specific part so that program doesnt recognize buff skill icon on skill bar or skill list and only checks buff icon location.
- Current buff cast waiting time is 3 seconds to be changed to be dynamic later on.
