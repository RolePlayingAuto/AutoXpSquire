# AutoXpSquire

Helper for your RPG fantasies to become the best Knight via Python

## Setup

- Run `pip install -r requirements.txt`

- Run the script via admin cmd or powershell  `python main.py`

## Usage
- Save Settings if you want any changes to be loaded in next start.
- Optionally put skill images in  `static/` folder with accordance to `config/skilldata_config.yml`and with `{class_name}_{skill_type}_{skill_name}.png` format. It would be better if you crop the images from your resolution for any image matching script uses.
- Edit `config/skilldata_config.yml` to fit your game's classes and skills. Its there as an example template.

### Control 
- Set the `Game Window Name` for the target game you want to run
- `Start Auto-Attack` and `Enable HP/MP Check` and `Enable Auto Buff` can be ticked to be enabled when bot starts.
- `Start Bot` starts the bot.
- Stop bot via Alt-Tab `Stop Bot` button.
- Alternatively use `F11` to start and `ESC` to stop.

### Settings

#### HP-MP Settings
- Select the HP and MP bar regions.
- Enter auto pot thresholds and pot keys.

#### Attack Settings
- Enable basic auto attack and auto targeting if you want it in. Enter the target or basic attack key in lower case. Basic attack key is pressed before and after every skill. If the game you are using with enables basic attack with skill cast or doesnt have animation cancel with basic skill you should not use it.
- Classes and skills will be loaded from the `config/skill_data.yml` file. Enter any type of class skills and skills types in the file following example format to show your classes and skills here. Skill images can optionally be stored in `static/` folder to see them in GUI. Image names should follow `{class_name}_{skill_type}_{skill_name}.png` format.
- Tick the skills you want to be used, enter their skill bar shortcuts and skill slot shortcuts. Example Skill bar `F4` Slot `5`.
- You can select monster name coordinates and give a list of monster names to attack for whitelisting mobs so that it wont try to attack any mob outside the list. Seperates multiple mob names as `mob 1,mob 2`

#### Buff Settings
- For any buff skill to be recognized and cast, their template image needs to be in `static/` with correct naming.
- From the `Skill Settings` Tab tick the `buff` for any skill that you want registered as a buff. This will add the skill to `Buff Settings` Tab under `Settings` Tab.
- Tick the `Activate` for the buff that you want it to be checked for and cast.
- Under Settings -> Buff Settings click `Select Coordinates` and select the area you want the program to search for the buff icon. This is for you to select a specific part so that program doesnt recognize buff skill icon on skill bar or skill list and only checks buff icon location.
- Set the buff casting time (in miliseconds) and buff cooldowns (in seconds) at Settings -> Buff Settings, these are needed for smooth buffing and not try to buff while skill is on cooldown.

#### Heal Settings
- Similar to buff settings, from `Skill Settings` set the heal skills with the heal checkbox. Enable the ones you want on your rotation.
- Set the `Heal Threshold` for healing. Set HP/MP bar coordinates in HP/MP settings for check to work.
- Set the cooldown and cast time for skills and `Save Settings`

## Disclaimer
- This script is meant to use in a SinglePlayer game or on your own servers. Don't use it to cheat on online games or break TOS.
