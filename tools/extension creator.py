import pick
import os
import shutil

# Get extensions folder and the base extension
extensions_dir = os.path.abspath("../extensions/active/")
base_extension = extensions_dir+"/base/"

print("Creating an Extension.")
extension_name = input("What is the name of your extension: ")

# Set possible options
options = [
    "Events",
    "Discord bot",
    "Web interface",
]
option_files = [
    "events.py",
    "bot.py",
    "web.py"
]

# Set selected and unselected symbols
pick.SYMBOL_CIRCLE_EMPTY = "○"
pick.SYMBOL_CIRCLE_FILLED = "●"
extension_files = pick.pick(options,
                       "What do you want to include in your extension. (Press SPACE to select, and ENTER to continue.)",
                       multiselect=True, indicator=">>")


if not os.path.exists(f"{extensions_dir}/{extension_name}"): os.mkdir(f"{extensions_dir}/{extension_name}")  # Create directory if it doesnt exist already
shutil.copy(f"{base_extension}/__init__.py", f"{extensions_dir}/{extension_name}/__init__.py")  # Copy __init__.py from base to new extension
for file in extension_files:
    if file[1] == "Web Interface":
        shutil.copytree(f"{base_extension}/templates", f"{extensions_dir}/{extension_name}/templates")  # Copy templates web interface is enabled

    if os.path.exists(f"{extensions_dir}/{extension_name}/{option_files[file[1]]}"): continue  # If the file exists we dont overwrite it.
    shutil.copy(f"{base_extension}/{option_files[file[1]]}", f"{extensions_dir}/{extension_name}/{option_files[file[1]]}")  # Copy the extension file from base to new extension

print("Successfully created the extension!")
os.system("pause")