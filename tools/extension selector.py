import os
import pick
import shutil

active_extensions = os.listdir("../extensions/active")
inactive_extensions = os.listdir("../extensions/inactive")

all_extensions = {i: {"active": True} for i in active_extensions}
for i in inactive_extensions: all_extensions[i] = {"active": False}

# Set selected and unselected symbols
pick.SYMBOL_CIRCLE_EMPTY = "○"
pick.SYMBOL_CIRCLE_FILLED = "●"

picker = pick.Picker(list(all_extensions), "Select extension(s) to activate..", multiselect=True, indicator=">>")
picker.selected_indexes = [list(all_extensions).index(i) for i in active_extensions]

selected = []
results = [i[0] for i in picker.start()]
new_states = {}
for i in all_extensions:
    if all_extensions[i]["active"] and i in selected:
        continue
    if not all_extensions[i]["active"] and i not in selected:
        continue
    new_states[i] = {"active": not all_extensions[i]["active"]}

for extension in new_states:
    if new_states[extension]["active"]:
        shutil.move(f"../extensions/inactive/{extension}", f"../extensions/active/{extension}")
    else:
        shutil.move(f"../extensions/active/{extension}", f"../extensions/inactive/{extension}")

print("Successfully done all changes, you can close this window now.")
os.system("pause" if os.name == "nt" else "read -p \"Press any key to continue . . .\"")
