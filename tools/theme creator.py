import pick
import os
import shutil
import json

# Get themes folder and the base theme
themes_dir = os.path.abspath("../themes/")
base_theme = themes_dir+"/baseTheme/"

print("Creating a theme.")
theme_name = input("What is the name of your theme: ")

# Set possible options
options = [
    "py",
    "txt"
]
option_files = [
    ["theme.py"],
    ["logo.txt", "printText.txt"]
]

mode, mode_idx = pick.pick(options=options, title="Please select your theme mode.", indicator=">>")

# Copy needed files
if not os.path.exists(f"{themes_dir}/{theme_name}"):  # Create directory if it doesnt exist already
    os.mkdir(f"{themes_dir}/{theme_name}")
if not os.path.exists(f"{themes_dir}/{theme_name}/config.json"):  # If the config exists we dont overwrite it.
    shutil.copy(f"{base_theme}/config.json", f"{themes_dir}/{theme_name}/config.json")

for file in option_files[mode_idx]:
    if os.path.exists(f"{themes_dir}/{theme_name}/{file}"):
        continue  # If the file exists we dont overwrite it.
    shutil.copy(f"{base_theme}/{file}", f"{themes_dir}/{theme_name}/{file}")

with open(f"{themes_dir}/{theme_name}/config.json", "r") as f:
    config = json.load(f)

config["title"] = input("Console window title: ")

with open(f"{themes_dir}/{theme_name}/config.json", "w") as f:
    json.dump(config, f, indent=4)

if pick.pick(["Yes", "No"], "Set theme as active theme?", indicator=">>")[0] == "Yes":
    with open("../config.json", "r") as f:
        config = json.load(f)
    config["current theme"] = theme_name
    with open("../config.json", "w") as f:
        json.dump(config, f, indent=4)

if pick.pick(["Yes", "No"], "Show all possible variables for themes?", indicator=">>")[0] == "Yes":
    print(f"The script will close once the notepad file is closed"
          f"\nNow showing {themes_dir}/required/required.json")
    os.system(f"notepad {themes_dir}/required/required.json")


print("Successfully created theme!")
os.system("pause")
