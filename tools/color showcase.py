import json
import os

with open("../themes/required/required.json", "r") as f:
    colours = json.loads(f.read())['colours']

os.system("cls" if os.name == "nt" else "clear")
message = input("Desired message (leave empty for base message): ")
if message == "": message = f"Lorem ipsum dolor sit amet"
for colour in colours:
    print(f"\x1b[38;5;{colours[colour]}m{message} - {colour}")

os.system("pause" if os.name == "nt" else "read -p \"Press any key to continue . . .\"")
