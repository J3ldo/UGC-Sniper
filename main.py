# Made by:
#   Original code, updates, and owner: @jeldo
#   Proxy support, fork, better UI, and developer: ! max#7948
VERSION = "3.0.1"
import os; os.system("cls" if os.name == "nt" else "clear")

try:
    print(f"\x1b[38;5;2mLoading modules...")
    import discord
    from discord.ext import commands
    import aiohttp
    import asyncio
    import traceback
    import ctypes
    import json
    import time
    import uuid
    import copy
    import datetime
    from itertools import cycle
    from pick import pick
    import rgbprint
    import math
    import logging
    import logging.config
    import hashlib
    import importlib
    try: import rapidjson as json
    except ImportError: import json
    try: import quart
    except ImportError: pass
    import subprocess
    import re
    import random
    print(f"\x1b[38;5;2mModules loaded!")

    # Import the base extension
    # from extensions.base import *
except ModuleNotFoundError:
    import os

    try:
        from pick import pick

        install = pick(["Yes", "No"], "Uninstalled modules found, do you want to update?", indicator=">>")[1] == 0
    except ModuleNotFoundError:
        install = input("Uninstalled modules found, do you want to install them? Y/N\n>> ").lower() == "y"

    if install:
        print("Required modules not installed, installing now...")
        os.system("python -m pip install --upgrade pip")
        os.system("pip install aiohttp");os.system("python -m pip install aiohttp");os.system("py -m pip install aiohttp")
        os.system("pip install pick");os.system("python -m pip install pick");os.system("py -m pip install pick")
        os.system("pip install rgbprint");os.system("python -m pip install rgbprint");os.system("py -m pip install rgbprint")
        os.system("pip install discord.py");os.system("python -m pip install discord.py");os.system("py -m pip install discord.py")
        os.system("pip install python-rapidjson");os.system("python -m pip install python-rapidjson");os.system("py -m pip install python-rapidjson")
        os.system("pip install quart==0.17.0");os.system("python -m pip install quart==0.17.0");os.system("py -m pip install quart==0.17.0")
        print("Successfully installed required modules.")
    else:
        print("Aborting installing modules.")

    os.system("pause" if os.name == "nt" else "read -p \"Press any key to continue . . .\"")
    exit(1)

os.system("cls" if os.name == "nt" else "clear")
if os.name == "nt":
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("J3ldo Sniper")
    except:
        pass

if not os.path.exists("./logs"): os.mkdir("./logs")
# logging.config.dictConfig({'version': 1,'disable_existing_loggers': True})
logging.basicConfig(filename=f"./logs/logs {str(datetime.datetime.now())[:-10].replace(':', '')}.txt",
                    level=logging.INFO, format="%(asctime)s:%(levelname)s-%(module)s  %(message)s")
logging.info("Started")

# Load the config
with open('config.json', "r") as f:
    conf = json.load(f)

# Global variables
recent_logs = []
all_logs = []
runtime_start = time.time()


class Visual:
    @staticmethod
    def betterPrint(content, print_log=False, log=True, log_level="info", include_time=True):
        now = f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')}] " if include_time else ""
        if log:
            all_logs.append(Visual.removeColour(f"{now}{content}"))
            exec('logging.' + log_level + '(f"{content}")')
        if conf["better print"] and print_log:
            recent_logs.append(f"[COLOR_LIGHT_BLUE]{now}{content}")
            return

        if Visual.__parsegradient(content) == 0:
            print(Visual.textToColour(f"[COLOR_LIGHT_BLUE]{now}{content}"))

    @staticmethod
    def add_log(content, include_time=True):
        now = f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')}] " if include_time else ""
        all_logs.append(Visual.removeColour(f"{now}{content}"))

    @staticmethod
    def __parsehex(text):
        txt = text.split("[HEX_")
        if len(txt) == 1:
            return txt[0]

        text = txt[0]
        for i in txt[1:]:
            i = i.split("]")
            text += f"{rgbprint.Color(i[0])}{''.join(i[1:])}"

        return text

    @staticmethod
    def __parsergb(text):
        txt = text.split("[RGB_")
        if len(txt) == 1:
            return txt[0]

        text = txt[0]
        for i in txt[1:]:
            i = i.split("]")
            r, g, b = i[0].split(",")
            text += f"{rgbprint.Color((int(r), int(g), int(b)))}{''.join(i[1:])}"

        return text

    @staticmethod
    def __parsegradient(text):  # Meest leesbaar stukje programma in de wereld
        if "[GRADIENT" not in text:
            return 0
        try:
            txt = text.split("[GRADIENT_")
            print(txt[0], end="")
            for i in txt[1:]:
                start, end = i.split("]")[0].split("_")
                toprint, other = i.split("[END]")
                toprint = "".join(toprint.split("]")[1:])
                rgbprint.gradient_print(toprint, start_color=start, end_color=end, end="")
                print(other, end="")
        except IndexError:
            Visual.betterPrint("[COLOR_RED]Syntax error whilst decoding gradients.")
            Visual.pause()
            exit(1)

        return 1

    @staticmethod
    def removeColour(text: str):
        if "COLOR" in text:
            for key in theme_info["colours"]:
                text = text.replace(key, "")

        return text

    @staticmethod
    def textToColour(text: str):
        if "COLOR" in text:
            for key in theme_info["colours"]:
                text = text.replace(key, f"\x1b[38;5;{theme_info['colours'][key]}m")

        try:
            if "[HEX" in text:
                text = Visual.__parsehex(text)
        except IndexError:
            Visual.betterPrint("[COLOR_RED]Syntax error whilst decoding hex.")
            Visual.pause()
            exit(1)

        try:
            if "[RGB" in text:
                text = Visual.__parsergb(text)
        except IndexError:
            Visual.betterPrint("[COLOR_RED]Syntax error whilst decoding RGB.")
            Visual.pause()
            exit(1)

        return text

    @staticmethod
    def textToVar(sniper, text: str):
        if type(sniper) != UGCSniper:
            Visual.betterPrint("[COLOR_RED] WARNING, NO VALID SNIPER PASSED TO textToVar")
            Visual.pause()
            exit(1)

        custom_vars = {
            "[username]": sniper.userinfo["name"],
            "[displayName]": sniper.userinfo["displayName"],
            "[userId]": sniper.userinfo["id"],

            "[proxiesEnabled]": False,
            "[proxyAmount]": len(sniper.proxies_raw),
            "[currentProxy]": sniper.proxy,
            "[changedProxies]": sniper.proxies_switched,
            "[ratelimits]": sniper.ratelimits,

            "[time]": sniper._time,
            "[limitedsAmount]": len(sniper.limiteds),
            "[limiteds]": ", ".join(sniper.limiteds),
            "[speed]": sniper.speed,
            "[status]": sniper.stats,
            "[priceChecks]": sniper.checks_made,
            "[bought]": sniper.bought,
            "[boughtpaid]": sniper.boughtpaid,

            "[ip]": sniper.ip,
            "[tooltip]": sniper.tooltip,
            "[memory_usage]": sniper.ram,  # Disabled when needed for preformance purposes
            "[cpu_usage]": "N/A",
            "[network_strength]": "N/A",
            "[network_receive]": "N/A",
            "[netowrk_transmit]": "N/A",

            "[x-csrf]": sniper.cookies[0][1],
            "[cooldown]": sniper.cooldown,
            "[errors]": sniper.errors,
            "[version]": VERSION,
            "[mode]": sniper.mode,
            "[logs]": "".join(themeConfig.get('log seperator', "[LOG]\n").replace("[LOG]", log) for log in recent_logs),
            "[runtime]": round(time.time()-runtime_start, 2)
        }
        if "[network_strength]" in text or "[network_receive]" in text or "[netowrk_transmit]" in text:
            interface_info = subprocess.getoutput("netsh wlan show interfaces")
            custom_vars["[network_strength]"] = interface_info.split("Signal                 : ")[1].split("%")[0]
            custom_vars["[network_transmit]"] = interface_info.split("Transmit rate (Mbps)   :")[1].splitlines()[0]
            custom_vars["[network_receive]"] = interface_info.split("Receive rate (Mbps)    : ")[1].splitlines()[0]

        for key in custom_vars:
            text = text.replace(key, str(custom_vars[key]))

        return text

    @staticmethod
    def pause():
        os.system("pause" if os.name == "nt" else "read -p \"Press any key to continue . . .\"")

    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

class Other:
    @staticmethod
    def calculate_cooldown(reqs_per_min, mode):
        try:
            cooldown = 60 / reqs_per_min
        except ZeroDivisionError:
            Visual.betterPrint("[COLOR_RED]No limiteds added, please add a limited for the sniper to work.")
            Visual.pause()
            exit(1)

        cooldown = conf.get(f"custom {mode} cooldown", -1) if conf.get(f"custom {mode} cooldown", -1) >= 0 else cooldown
        return cooldown

    @staticmethod
    async def handle_ratelimit(sniper, log, custom_cooldown=-1, text="", no_switch=False):
        cooldown = conf['proxy ratelimit cooldown'] if sniper.proxiesOn else conf['ratelimit cooldown']
        if custom_cooldown >= 0: cooldown = custom_cooldown

        if text == "": text = f"[COLOR_RED]Ratelimit continuing in {cooldown} seconds."
        Visual.betterPrint(f"{text} - {log}", True)

        # Run ratelimit event tasks
        for task in ratelimit_tasks: task()

        await asyncio.sleep(cooldown)
        if sniper.proxiesOn and not no_switch:
            sniper.proxy = next(sniper.proxy_pool)
            sniper.proxies_switched += 1
            return False, [], [], True

        sniper.ratelimits += 1
        return False, [], [], True


# Load theme
with open("themes/required/required.json", "r") as f:
    theme_info = json.load(f)

themeVersion = "1.4.0"

themeLocation = "./themes/" + conf["current theme"]
with open(themeLocation + "/config.json", "r") as f:
    themeConfig = json.load(f)
if themeConfig["version"] != themeVersion:
    Visual.betterPrint(f"[COLOR_RED]DEPRECTATION WARNING - Version of the theme is deperecated, theme may not work.\n"
                       f"Do you still want to continue?[COLOR_WHITE]")
    if pick(["Yes", "No"], "", indicator=themeConfig.get("indicator", ">>"))[1] == 1:
        exit(1)

if themeConfig["type"] not in theme_info["types"]:
    Visual.betterPrint(f"[COLOR_RED]Theme has invalid type, types can only be {' or'.join(theme_info['types'])[:-3]}")

if themeConfig["type"] == "py":
    with open("themes/required/whitelisted.hash", "r") as f:
        with open(f"{themeLocation}/{themeConfig['script']}", "rb") as con:
            stop = hashlib.sha256(con.read()).hexdigest() in f.read().split(";")

    if not conf.get("allowPyThemes", False) and not stop:
        print(Visual.textToColour("[COLOR_LIGHT_BLUE]"), end="\n")
        idx = pick(["Yes", "Yes, and dont warn me again.", "Yes, and whitelist this theme", "No",
                    "No, and show me more information about this program"],
                   f"WARNING The theme you are trying to use is using scripts to run, do you want to continue?",
                   indicator=themeConfig.get("indicator", ">>"))[1]
        if idx == 3:
            Visual.pause()
            exit(1)
        if idx == 1:
            conf["allowPyThemes"] = True
            with open('config.json', "w") as f:
                json.dump(conf, f, indent=4)
        if idx == 2:
            with open("themes/required/whitelisted.hash", "a") as f:
                with open(f"{themeLocation}/{themeConfig['script']}", "r") as con:
                    f.write(hashlib.sha256(con.read().encode()).hexdigest() + ";")
        if idx == 4:
            with open(themeLocation[2:] + "/" + themeConfig["script"], "rb") as f:
                file_content = f.read()
            # TO-DO
            # Get imports
            # Get lines of code
            # Get other functions

            imports = ""
            for i in file_content.split("import "):
                imports += f"\t{i.splitlines()[0].replace('from ', '')}\n"

            print(Visual.textToColour(f"[COLOR_LIGHT_BLUE] All imports: \n{imports}\n"
                                      f"[COLOR_GREEN]Lines of code: {len(file_content.splitlines())}\n\n"
                                      f"[COLOR_WHITE]"))

            Visual.pause()
            exit(1)

    themeFile = importlib.import_module(themeLocation.replace("/", ".")[2:] + "." + themeConfig["script"][:-3])

if os.name == "nt":
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(themeConfig["title"])
    except:
        pass
if os.name == "nt" and themeConfig.get("resize", {"width": -1, "height": -1}) != {"width": -1, "height": -1}:
    os.system(f"mode con: cols={themeConfig['resize']['width']} lines={themeConfig['resize']['height']}")

# Load themes info
with open(f"{themeLocation}/{themeConfig['logo']}", "r", encoding="unicode_escape") as f: logo = Visual.textToColour(
    f.read())
with open(f"{themeLocation}/{themeConfig['printText']}", "r",
          encoding="unicode_escape") as f: printText = Visual.textToColour(
    f.read())

update_freq = -1
frames = []
current_frame = "N/A"
if themeConfig.get("animated", False):
    for i in range(1, 60):  # Max frames
        try:
            with open(f"{themeLocation}/{themeConfig['frames']}/frame_{i}.txt") as f:
                frames.append(f.read())
        except FileNotFoundError:
            break
    if len(frames) > 0:
        update_freq = 1 / themeConfig['fps']
        frame_pool = cycle(frames)
        current_frame = next(frame_pool)

# Load extensions

# Initialize the start, iteration, and end tasks. These dont want to be overwritten
start_tasks = []
iteration_tasks = []
end_tasks = []
error_tasks = []
buy_tasks = []
start_buy_tasks = []
ratelimit_tasks = []

for module in os.listdir("./extensions/active"):
    contents = ""
    for script in os.listdir(f"./extensions/active/{module}"):
        if os.path.isdir(f"./extensions/active/{module}/{script}"): continue
        with open(f"./extensions/active/{module}/{script}", "r") as f:
            contents += f.read()

    module_hash = hashlib.sha256(contents.encode()).hexdigest()
    with open("./extensions/required/trustedExtensions.hash", "r") as f:
        trustedhashes = f.read().split(";")
    if module_hash not in trustedhashes and not conf.get("trustExtensions", False):
        print(Visual.textToColour("[COLOR_RED]"), end="")
        idx = pick(["Yes", "Yes, and dont warn me again.", "Yes, and whitelist this extension", "No"],
                   f"WARNING - Unknown extension found. Do you want to continue? - Extension: {module}",
                   indicator=conf.get("indicator", ">>"))[1]
        if idx == 1:
            conf["trustExtensions"] = True
            with open("config.json", "w") as f:
                json.dump(conf, f, indent=4)
        if idx == 2:
            with open("./extensions/required/trustedExtensions.hash", "a") as f:
                f.write(module_hash + ";")

        if idx == 3:
            Visual.pause()
            exit(1)

    module = importlib.import_module(f"extensions.active.{module}")
    if hasattr(module, '__all__'):
        all_names = module.__all__
    else:
        all_names = [name for name in dir(module) if not name.startswith('_')]

    # Get the start, iteration, and end functions. These dont need to be overwritten for multiple extensions
    if "start" in dir(module): start_tasks.append(module.start)
    if "iteration" in dir(module): iteration_tasks.append(module.iteration)
    if "end" in dir(module): end_tasks.append(module.end)
    if "on_load" in dir(module): module.on_load()
    if "error" in dir(module): error_tasks.append(module.error)
    if "buy" in dir(module): buy_tasks.append(module.buy)
    if "start_buy" in dir(module): start_buy_tasks.append(module.start_buy)
    if "ratelimit" in dir(module): ratelimit_tasks.append(module.ratelimit)

    globals().update({name: getattr(module, name) for name in all_names})

print(Visual.textToColour(f"[COLOR_LIGHT_BLUE]UGC-Sniper made by: @jeldo (J3ldo) and ! max#7948 (maxhithere)\n"
                          f"[COLOR_LIGHT_BLUE]Discord server: https://discord.com/invite/3Uvcf8d9aY)"))
time.sleep(1)

class UGCSniper:  # OMG guys he stole this from xolo!!
    def __init__(self):
        Visual.clear()
        if os.name == "nt": asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Init data
        self.errors = 0
        self._time = 0
        self.speed = 0
        self.bought = 0
        self.boughtpaid = 0
        self.checks_made = 0
        self.ratelimits = 0
        self.proxies_switched = 0
        self.stats = "N/A"
        self.proxy = "N/A"
        self.version = VERSION
        self.ram = 0

        self.finder_added = 0
        self.finder_blacklist = []

        self.limiteds = []
        self.limitednames = {_id: "N/A" for _id in self.limiteds}
        self.ip = ""
        self.tooltips = [
            "You can set custom cooldowns in the config.",
            "Starting the sniper can be made fully automatic using the right config.",
            "There are a lot of handy tools in the tools folder like an extension selector, and more.",
            "Discord .gg/J3ldo to chat with the community",
            "You can put in limiteds the following ways: id, id or id[enter/newline]id",
            "You can put in multiple cookies so you dont use your main cookie for checking.",
            "Links are supported in limiteds.txt"
        ]+themeConfig.get("custom tooltips", [])
        self.tooltip = random.choice(self.tooltips)

        self.mode = ""
        self.mode_time = False
        self.minutes = int(conf["time wait minutes"])
        self.unix = math.floor(conf["time wait unix"])
        self.cooldown = 0

        self.userinfo = {}
        self.update_token = False
        asyncio.run(self.auto_update())
        self.get_info()

        self.load_limiteds()
        self.limitednames = {_id: "N/A" for _id in self.limiteds}

        self.load_proxies()
        self.get_type()

    def get_info(self):
        self.cookies = [[i, ""] for i in conf["cookie"]]
        if type(conf["cookie"]) != str: return
        with open(conf["cookie"], "r") as f:
            self.cookies = [[i, "", 0] for i in f.read().replace(";", "").splitlines()]

    def load_limiteds(self):
        self.limiteds = conf["limiteds"]
        if type(self.limiteds) != str:
            return
        with open(conf["limiteds"], "r") as f:
            contents = f.read()

            if "/catalog/" in contents:
                self.limiteds = [re.findall(r"/catalog/[0-9]+", contents)[0].split("/")[-1]]
            else:
                self.limiteds = contents.replace(" ", "").splitlines()
                if "," in contents:
                    self.limiteds = contents.replace(" ", "").split(",")

    def proxy_cycle(self):
        idx = 0
        while 1:
            yield self.proxies_raw[idx]
            idx += 1
            if idx > len(self.proxies_raw)-1:
                idx = 0


    async def check_proxies(self):
        async def is_working(session, proxy):
            '''
            :param session: The aiohttp session
            :param proxy: The proxy url

            :return: bool working
            '''
            try:
                working = await session.get("http://users.roblox.com/v1/users/authenticated", ssl=False, proxy=proxy[0],
                                            timeout=conf.get("timeout", 3))
                if working.status == 401:
                    resp = await session.get(f"http://ip-api.com/json/", ssl=False, proxy=proxy[0],
                                             timeout=conf.get("timeout", 3))
                    data = json.loads(await resp.text())

                    spacing = " " * (50 - len(f"{data['country']} ({data['regionName']})"))
                    print(Visual.textToColour(
                        f"[COLOR_GREEN][+] Working proxy in [COLOR_WHITE]{data['country']} ({data['regionName']})[COLOR_GREEN]  {spacing}Proxy: {proxy[0]}"))

                    self.proxies_raw.append(proxy)
                    return True
            except aiohttp.client_exceptions.InvalidURL:
                new_prox = proxy[0].split(":")
                proxy[0] = ""
                for idx, item in enumerate(new_prox):
                    if idx == len(new_prox) - 2:
                        proxy[0] += "@" + item
                    elif idx == 0:
                        proxy[0] += item
                    else:
                        proxy[0] += ":" + item
                if proxy[0] == "" or proxy[0] == ":": return False

                return await is_working(session, proxy)
            except:
                return False

            return False

        chunks = [self.proxies_raw[i:i + 500] for i in range(0, len(self.proxies_raw), 500)]
        self.proxies_raw = []
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None),
                                         json_serialize=json.dumps,
                                         trust_env=True) as s:

            for chunk in chunks:
                tasks = []
                for proxy in chunk:
                    tasks.append(asyncio.create_task(is_working(s, proxy)))

                await asyncio.gather(*tasks)

    def load_proxies(self):
        with open(conf["proxies"], "r") as f:
            self.proxies_raw = [["http://" + proxy, ""] if "http" not in proxy else [proxy, "x-csrf-token"] for proxy in f.read().splitlines()]
            self.proxiesOn = bool(self.proxies_raw) and conf["proxies enabled"]
            self.proxy = "N/A"

            if self.proxiesOn:
                if conf["checkProxies"]:
                    print(Visual.textToColour("[COLOR_LIGHT_BLUE]"), end="")
                    idx = pick(["Yes", "Yes, and save the working proxies.", "No", "No, and don't remind me again"],
                               "Proxies found, do you want to check them?",
                               indicator=themeConfig.get('indicator', ">>"))[1]
                    if idx == 0 or idx == 1:
                        asyncio.run(self.check_proxies())
                    if idx == 1:
                        with open(conf["proxies"], "w") as f:
                            f.write("\n".join(self.proxies_raw))
                    if idx == 1 or idx == 3:
                        conf["checkProxies"] = False
                        with open("config.json", "w") as f:
                            json.dump(conf, f, indent=4)

                if len(self.proxies_raw) == 0:
                    return

                self.proxy_pool = self.proxy_cycle()
                self.proxy = next(self.proxy_pool)

    async def auto_update(self):
        async with aiohttp.ClientSession() as s:
            try:
                self.ip = json.loads(await (await s.get("http://www.httpbin.org/ip", timeout=2)).text())["origin"]
            except:
                self.ip = "N/A"

        if not conf["auto update"] or conf.get("update reminder", 0) > time.time():
            return
        Visual.betterPrint("[COLOR_AQUAMARINE_1A]Checking for potential updates...")
        async with aiohttp.ClientSession() as s:
            src = await (await s.get("https://raw.githubusercontent.com/J3ldo/UGC-Sniper/main/main.py", ssl=False)).text()
        try:
            version = src.split("VERSION = \"")[1].split("\"")[0]
        except IndexError:
            visual.betterPrint("[COLOR_RED]Could not get valid version number")
            version = VERSION

        if version != VERSION:
            idx = pick(["Yes", "No", "No, and don't remind me again", "No, Remind me in 30 minutes"],
                       Visual.textToColour("New update found, do you want to update?"),
                       indicator=themeConfig.get("indicator", ">>"))[1]
            if idx == 1:
                return
            if idx == 2:
                conf["auto update"] = False
                with open('config.json', "w") as f:
                    json.dump(conf, f, indent=4)
                return
            if idx == 3:
                conf["updateReminder"] = math.floor(time.time()) + 30 * 60
                with open('config.json', "w") as f:
                    json.dump(conf, f, indent=4)
                return
            Visual.betterPrint("[COLOR_AQUAMARINE_1A]Updating code...")
            with open("main.py", "w", encoding="utf-8") as f:
                f.write(src)
            Visual.betterPrint("[COLOR_AQUAMARINE_1A]Updated code! restart the sniper to use the newest version")
            Visual.pause()
            exit(0)
        else:
            Visual.betterPrint("[COLOR_AQUAMARINE_1A]No updates found.")

    def get_type(self):
        modes = ["Speed 1-2 minutes  before ratelimit", "Quick 2-10 minutes before ratelimit", "Casual 10-60 minutes before ratelimit",
                 "Afk 1-12 hours before ratelimit", "Time 1-∞ minutes before ratelimit", "Specific time 1-∞ minutes before ratelimit"]
        modeNames = ["Speed", "Quick", "Casual", "Afk", "Time", "Specific time"]

        self.mode = conf.get("mode", "").title()
        if self.mode not in modeNames:
            self.mode = modeNames[
                pick(modes, "Select your checking mode: ", indicator=themeConfig.get("indicator", ">>"))[1]]

        if self.mode == "Speed":
            self.cooldown = Other.calculate_cooldown(80, self.mode.lower())

        elif self.mode == "Quick":
            self.cooldown = Other.calculate_cooldown(60, self.mode.lower())

        elif self.mode == "Casual":
            self.cooldown = Other.calculate_cooldown(55, self.mode.lower())

        elif self.mode == "Afk":
            self.cooldown = Other.calculate_cooldown(50, self.mode.lower())

        elif self.mode == "Time":
            self.mode_time = True
            if self.minutes < 0:
                Visual.betterPrint("[COLOR_LIGHT_BLUE][>>] Enter number of minutes untill ugc releases: ")
                self.minutes = int(input(Visual.textToColour("[COLOR_LIGHT_BLUE]   [>>] ")))
            Visual.betterPrint(
                f"[COLOR_VIOLET][*] Sniper will run for {self.minutes} minutes / {self.minutes * 60} seconds before speed sniping")
            time.sleep(3)

            self.cooldown = conf["custom time cooldown"] if conf["custom time cooldown"] >= 0 else 0.5
            if len(self.limiteds) == 0:
                Visual.betterPrint("[COLOR_RED]No limiteds added, please add a limited for the sniper to work.")
                Visual.pause()
                exit(1)
        else:
            while 1:
                if self.unix < 0:
                    Visual.betterPrint("[COLOR_LIGHT_BLUE][>>] Enter the unix timestamp of when the item releases.")
                    self.unix = math.floor(float(input(Visual.textToColour("[COLOR_LIGHT_BLUE]   [>>] "))))
                self.minutes = math.floor((self.unix - time.time()) / 60)
                if self.minutes < 0:
                    Visual.betterPrint(
                        "[COLOR_RED]WARNING The specified unix timestamp already happend, please put in a valid timestamp.")
                    time.sleep(1)
                    self.unix = -1
                    Visual.clear()
                    continue
                break

            Visual.betterPrint(
                f"[COLOR_LIGHT_BLUE]Will start sniping in {self.minutes} minutes or on {datetime.datetime.fromtimestamp(self.unix)}")
            time.sleep(3)
            self.mode_time = True
            self.cooldown = conf["custom unix cooldown"] if conf["custom unix cooldown"] >= 0 else 0.5

    async def wait(self):
        if self.minutes <= 0:
            return
        if self.mode_time is True:
            Visual.betterPrint(
                "[COLOR_AQUAMARINE_1A]You picked time. Feel the essence of the sniper and the power of the limiteds. The great fortunes you can make, just by waiting..")
        Visual.betterPrint(f"[COLOR_PINK_1][*] You have {self.minutes} minutes left.")

        async with aiohttp.ClientSession() as s:
            for i in range(self.minutes):
                fact = json.loads(await (await s.get("https://catfact.ninja/fact")).text())["fact"]
                for _ in range(60):
                    if self.minutes <= 0:
                        Visual.betterPrint("[COLOR_CYAN]Unpaused.")
                        return
                    await asyncio.sleep(1)

                Visual.betterPrint(f"[COLOR_PINK_1][*] You have {self.minutes - (i + 1)} minutes left.\n"
                                   f"\t[COLOR_CYAN]Random cat fact: {fact}")

        Visual.betterPrint(f"[COLOR_PINK_1][*] Time ended. Starting spam sniper.")

    def start(self):
        for task in start_tasks: asyncio.run(task(self))
        asyncio.run(self.main())

    async def print_all(self):
        global recent_logs, current_frame
        iteration = 0
        if themeConfig["type"] == "txt": Visual.betterPrint(logo, log=False)
        if themeConfig["type"] == "py":
            if themeFile.printLogo() == 0:
                sniper.errors += 1

        while 1:
            if iteration > conf.get("log reset iteration", 3)*themeConfig.get("fps", 1):
                iteration = 0
                self.tooltip = random.choice(self.tooltips)
                self.ram = subprocess.getoutput(f'tasklist /fi "pid eq {os.getpid()}"').split(" K")[0].split(" ")[
                -1] if "[memory_usage]" in printText else "N/A"  # Preformance go brr
                recent_logs = []

            Visual.clear()
            if themeConfig["type"] == "py":
                if conf.get("logo dupe", True):
                    if themeFile.printLogo() == 0: sniper.errors += 1

                if themeFile.printText(sniper, "".join(
                    themeConfig.get('log seperator', "[LOG]\n").replace("[LOG]", log) for log in recent_logs)) == 0:
                    sniper.errors += 1

            if themeConfig["type"] == "txt":  # Text theme
                if update_freq < 0:  # Not animated
                    if conf.get("logo dupe", True): Visual.betterPrint(logo, log=False, include_time=False)
                else:  # Animated
                    Visual.betterPrint(current_frame, log=False, include_time=False)
                    current_frame = next(frame_pool)
                Visual.betterPrint(Visual.textToVar(self, printText), log=False, include_time=False)  # Print information

            if update_freq < 0:
                await asyncio.sleep(conf["print update cooldown"])
            else:
                await asyncio.sleep(update_freq)
            iteration += 1

    async def debug_print(self):
        global recent_logs

        Visual.betterPrint("[COLOR_GREEN]Successfully started debug print")
        while 1:
            if recent_logs:
                Visual.betterPrint("\n".join(recent_logs), include_time=False)
                recent_logs = []
            await asyncio.sleep(0.1)

    async def get_token(self):
        logging.info("Started getting token.")

        async with aiohttp.ClientSession(json_serialize=json.dumps) as s:
            self.userinfo = await (await s.get("https://users.roblox.com/v1/users/authenticated",
                                               cookies={".ROBLOSECURITY": self.cookies[0][0]})).json()
            for idx, cookie in enumerate(self.cookies):
                try:
                    self.cookies[idx][2] = (await (await s.get("https://users.roblox.com/v1/users/authenticated",
                                                               cookies={".ROBLOSECURITY": cookie[0]}, ssl=False)).json())['id']
                except KeyError:
                    Visual.betterPrint("[COLOR_RED]Invalid cookie parsed.")
                    Visual.pause()
                    exit(1)

            while 1:
                for idx, cookie in enumerate(self.cookies):
                    if idx == 0 and self.update_token: self.update_token = False

                    try:
                        resp = await s.post("https://auth.roblox.com/v2/logout",
                                            cookies={".ROBLOSECURITY": cookie[0]}, ssl=False)
                        self.cookies[idx][1] = resp.headers['x-csrf-token']
                    except:
                        self.update_token = True
                        break
                    logging.info(f"Got token of {self.cookies[idx][1]}")

                for _ in range(round(30)):
                    if self.update_token:
                        break
                    await asyncio.sleep(1)

    async def proxy_token(self):
        async with aiohttp.ClientSession() as s:
            async def get_token(idx):
                try:
                    self.proxies_raw[idx][1] = (await s.post("https://auth.roblox.com/v1/usernames/validate",
                                                proxy=self.proxies_raw[idx][0], timeout=conf.get("timeout", 3), proxy_auth=None)).headers['x-csrf-token']
                except:
                    self.errors += 1
                    return

            while 1:
                tasks = []
                for idx, proxy in enumerate(self.proxies_raw):
                    if idx == 0 and self.update_token: self.update_token = False
                    tasks.append(asyncio.create_task(get_token(idx)))
                await asyncio.gather(*tasks)

                for _ in range(round(30)):
                    if self.update_token:
                        break
                    await asyncio.sleep(1)

    async def get_bought(self, session, limited, cookie):
        try:
            req = await session.get(
                f"https://inventory.roblox.com/v2/users/{cookie[2]}/inventory/{limited['assetType']}?limit=100&sortOrder=Desc",
                cookies={".ROBLOSECURITY": cookie[0] if not self.proxiesOn else ""},
                headers={"x-csrf-token": cookie[0] if not self.proxiesOn else self.proxy[1]},
                ssl=False, proxy=self.proxy[0] if self.proxiesOn else "", timeout=conf.get("timeout", 3), proxy_auth=None)
        except asyncio.exceptions.TimeoutError:
            Visual.betterPrint("[COLOR_RED]Buy ratelimit caught! (timeout)", True)
            return -1

        return (await req.text()).count(str(limited["id"]))

    async def __buy(self, session, buydata, liminfo, cookie):
        '''
        :param session: The aiohttp.ClientSession
        :param buydata: The data needed for the buy request

        :return: bool bought, bool ratelimit, bool switch_cookie, bool soldout, dict data
        '''

        try:
            req = await session.post(
                f"https://apis.roblox.com/marketplace-sales/v1/item/{buydata['collectibleItemId']}/purchase-item",
                json=buydata, ssl=False, proxy=self.proxy[0] if self.proxiesOn and conf["purchase proxy"] else "",
                headers={"x-csrf-token": cookie[1] if not self.proxiesOn else self.proxy[1]},
                cookies={".ROBLOSECURITY": cookie[0] if not self.proxiesOn else ""},
                timeout=conf.get("timeout", 3), proxy_auth=None)

        except asyncio.exceptions.TimeoutError:
            Visual.betterPrint("[COLOR_RED]Buy ratelimit caught! (timeout)", True)
            return False, True, False, False, {}

        logging.info(f"Received: {await req.text()} - Sent : {buydata}")
        if req.reason == "Too Many Requests":
            Visual.betterPrint("[COLOR_RED]Buy ratelimit caught!", True)
            return False, True, False, False, {}

        data_raw = await req.text()
        if data_raw == "":
            Visual.betterPrint("[COLOR_RED]Caught Error whilst trying to get the buy information", True,
                               log_level="warning")
            self.errors += 1
            return False, False, False, False, {}

        try:
            data = json.loads(data_raw)
        except json.JSONDecodeError:
            Visual.betterPrint(
                f"[COLOR_RED]Caught Error whilst trying to get the buy information. Info: '{data_raw}' - {req.reason}",
                True, log_level="warning")
            self.errors += 1
            return False, False, False, False, {}

        if data['purchaseResult'] == 'Flooded':
            Visual.betterPrint("[COLOR_RED]Buy ratelimit caught!", True)
            return False, True, False, False, data

        if data['errorMessage'] == 'QuantityExhausted':
            Visual.betterPrint(f"[COLOR_RED]All items sold out.", True)
            return False, False, False, True, data

        if data['errorMessage'] == "Only support User type for purchasing: request purchaser type Group":
            Visual.betterPrint("[COLOR_RED]Limited is only available to buy from group.", True)
            return False, False, False, True, data

        if not data["purchased"]:
            Visual.betterPrint(f"[COLOR_RED]Failed buying limited, trying again.. Info: {data} - {buydata}", True)
            return False, False, False, False, data

        if data["purchased"]:
            Visual.betterPrint(f"[COLOR_AQUAMARINE_1A]Successfully bought limited! Info: {data} - {buydata}", True)
            if conf["webhook enabled"]:
                embed = discord.Embed(title='Purchased Limited', description=f'{"@everyone " if conf["ping everyone"] else ""}Successfully sniped a limited!',
                                      color=discord.Colour.blue())
                embed.add_field(name=f'Item',
                                value=f'[{liminfo["name"]}](https://www.roblox.com/catalog/{liminfo["id"]})')
                embed.add_field(name=f'Stock', value=f'`{liminfo["unitsAvailableForConsumption"]}/{liminfo["totalQuantity"]}`')
                embed.add_field(name=f'Received', value=f'{data}')

                webhook = discord.Webhook.from_url(conf["webhook"], session=session)
                await webhook.send(embed=embed)

            return True, False, False, False, data

        return False, False, False, False, data

    async def buy(self, session, data, dont_remove=False):
        '''
        :param session: The aiohttp session
        :param data: The item information received by the request

        :return: bool boughtsession
        '''
        logging.info("Buying item, got: "+str(data))
        for task in start_buy_tasks: asyncio.create_task(task(self, data["id"], data))
        if dont_remove is False:
            try:
                self.limiteds.remove(str(data["id"]))
            except ValueError:
                logging.warning(f"Limited: {data['id']} not in limiteds, All data: {data}")

        # Paid checks
        if data["price"] > 0 and not conf.get("purchase paid ugcs", False):
            Visual.betterPrint(f"[COLOR_RED]Aborted buying limited. Reason: paid limited - Price: {data['price']}",
                               True)
            return
        if data["price"] > conf.get("paid ugcs max price", 0):
            Visual.betterPrint(
                f"[COLOR_RED]Aborted buying limited. Reason: item price to high - Price: {data['price']}", True)
            return
        if data["price"] > 0 and self.boughtpaid >= conf.get("purchase paid ugcs amount", 0):
            Visual.betterPrint(
                f"[COLOR_RED]Aborted buying limited. Reason: Maximum amount of paid limiteds bought. - Price: {data['price']}",
                True)
            return

        # Get the product id
        productid = None
        Visual.betterPrint("Getting needed information...", True)
        while productid is None:
            _inf = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                      json={"itemIds": [data["collectibleItemId"]]}, ssl=False)

            try:
                Visual.betterPrint("Sent request for information, scraping needed information")
                inf = json.loads(await _inf.text())[0]
                productid = inf["collectibleProductId"]

            except (json.JSONDecodeError, KeyError):
                Visual.betterPrint(
                    f"[COLOR_RED]Something went wrong whilst getting the product id Logs - {await _inf.text()} - {_inf.reason}. Trying again.",
                    True)
                continue

        # Set up the data
        Visual.betterPrint("Got needed information, setting up data", True)
        buydata = {
            "collectibleItemId": inf["collectibleItemId"],
            "expectedCurrency": 1,
            "expectedPrice": data["price"] if conf.get("purchase paid ugcs", False) else 0,
            "expectedPurchaserId": "id of the receiver",
            "expectedPurchaserType": "User",
            "expectedSellerId": data["creatorTargetId"],
            "expectedSellerType": data['creatorType'],
            "idempotencyKey": "random uuid4 string that will be your key or smthn",
            "collectibleProductId": productid
        }
        Visual.betterPrint("Set up data.", True)

        # Run buy tasks.
        for task in buy_tasks: asyncio.create_task(task(self, data["id"], data, buydata))

        boughtsession = 0
        limit = data.get("quantityLimitPerUser", 0) if data.get("quantityLimitPerUser", 0) > 0 else conf[
            "cookie bought max"]

        soldout = False
        while not soldout:
            for cookie in self.cookies:
                boughtsession = 0
                boughtbefore = 0

                buydata['expectedPurchaserId'] = cookie[2]

                if soldout:
                    break

                while not soldout:
                    tasks = []
                    get_bought = asyncio.create_task(self.get_bought(session, data, cookie))

                    for _ in range(4):
                        buydata["idempotencyKey"] = str(uuid.uuid4())
                        tasks.append(asyncio.create_task(self.__buy(session, copy.copy(buydata), data, cookie)))
                    ratelimit = False
                    for task in tasks:
                        task = await task
                        if task[0]:
                            boughtbefore = boughtsession
                            boughtsession += 1
                        if task[1]:
                            ratelimit = True
                        if task[2] and boughtsession < limit:
                            boughtbefore = boughtsession
                            boughtsession += 9e10

                        if task[3]:
                            soldout = True

                    if ratelimit:
                        Visual.betterPrint(
                            f"[COLOR_RED]Got into a ratelimit! Continuing in {conf.get('buy ratelimit cooldown', 0.1)} second..",
                            True)
                        await asyncio.sleep(conf.get('buy ratelimit cooldown', 0.1))

                    if boughtsession - boughtbefore >= limit:
                        boughtsession = 0
                        Visual.betterPrint("[COLOR_GREEN]Bought maximum amount of limiteds on account, switching cookies.")
                        break
                    if inf["price"] > 0:
                        self.boughtpaid += boughtsession - boughtbefore
                        if self.boughtpaid >= conf.get("purchase paid ugcs amount", 0):
                            Visual.betterPrint(
                                f"[COLOR_RED]Aborted buying limited. Reason: Maximum amount of paid limiteds bought.",
                                True)

                            return boughtsession

                    boughtbefore = boughtsession
                    boughtsession = await get_bought
                    self.bought += (boughtsession - boughtbefore)
                    logging.info(f"Bought. Before: {boughtbefore}, After: {boughtsession}, Total: {self.bought}")

        boughtbefore = boughtsession
        boughtsession = await self.get_bought(session, data, self.cookies[0])
        Visual.betterPrint(f"All items sold out. Purchased {boughtsession} limiteds", True)
        self.bought += boughtsession - boughtbefore

        return boughtsession

    async def is_onsale(self, session: aiohttp.ClientSession, limiteds, remove=True):
        '''
        :param session: aiohttp session
        :param limiteds: All the limiteds to get the info of.

        :return: bool item_on_sale, list resp_data, list all_data, bool skip_wait
        '''
        if len(limiteds) == 0:
            await asyncio.sleep(0.1)
            return False, [], [], True

        item_on_sale = False
        resp_data = []
        try:
            if self.proxiesOn:
                resp = await session.post("http://catalog.roblox.com/v1/catalog/items/details",
                                          json={"items": [{"itemType": "Asset", "id": int(limited)} for limited in
                                                          limiteds[119:]]}, ssl=False,
                                          headers={"x-csrf-token": self.proxy[1]}, cookies={},
                                          proxy=self.proxy[0], timeout=conf.get("timeout", 3),
                                          proxy_auth=None)
            else:
                resp = await session.post("http://catalog.roblox.com/v1/catalog/items/details",
                                          json={"items": [{"itemType": "Asset", "id": int(limited)} for limited in
                                                          limiteds[-119:]]},
                                          ssl=False, timeout=conf.get("timeout", 3))
        except (asyncio.exceptions.TimeoutError, aiohttp.client_exceptions.ClientHttpProxyError,
                aiohttp.client_exceptions.ClientOSError, aiohttp.client_exceptions.ClientResponseError,
                aiohttp.client_exceptions.ServerDisconnectedError) as e:
            return await Other.handle_ratelimit(sniper, [], 0 if not self.proxiesOn else -1,
                                                f"[COLOR_RED]Network error, continuing. Severity: Very low")

        dat = {}
        try:
            dat = json.loads(await resp.text())
            all_data = dat["data"]
        except (json.JSONDecodeError, KeyError):
            msg = dat.get("errors", [{}])[0].get("message", "")
            if msg == "": msg = dat.get("message", "")
            if msg == "Invalid asset type id.":
                Visual.betterPrint("[COLOR_RED]Found invalid limited, removing limited.")
                return False, [], [], True

            if msg == "Token Validation Failed":
                self.update_token = True
                if resp.headers.get("x-csrf-token") is not None:
                    if not self.proxiesOn: self.cookies[-1][1] = resp.headers['x-csrf-token']
                    else:
                        self.proxies_raw[self.proxies_raw.index(self.proxy)][1] = resp.headers['x-csrf-token']
                        self.proxy = self.proxies_raw[self.proxies_raw.index(self.proxy)]
                    self.update_token = True
                return await Other.handle_ratelimit(sniper, await resp.text(), 0, "Token outdated, updating the token.", no_switch=True)

            return await Other.handle_ratelimit(sniper, await resp.text())

        for limited in all_data:
            try: self.limitednames[str(limited['id'])] = limited['name']
            except KeyError: pass

            if limited.get("saleLocationType", "") == "ExperiencesDevApiOnly":
                Visual.betterPrint(
                    f"[COLOR_RED]Limited found was a game exclusive item, removed from list. Limited: {limited['id']}")
                if remove: self.limiteds.remove(str(limited["id"]))

            elif limited.get("collectibleItemId", "") != "":
                item_on_sale = True
                resp_data.append(limited)
                continue

        return item_on_sale, resp_data, all_data, False

    async def scanner(self, session: aiohttp.ClientSession):
        # raise NotImplementedError("Not implemented this update.")
        '''
        :param session: aiohttp session
        '''

        cooldown = 60/35
        username = conf.get("scanner user id watching", -1)
        if username == -1:
            return
        if type(username) == int:  # gebruikersnaam > id // Holy shit ik heb een natuurkundetoets.
            username = json.loads((await (await session.get(f"https://users.roblox.com/v1/users/{username}")).text()))['name']

        async def get_items(user: str):
            '''

            :param user: The username of the watching user
            :return: items, ratelimit
            '''
            try:
                return [i['id'] for i in json.loads(await (await session.get(
                    f"https://catalog.roblox.com/v1/search/items?category=All&creatorName={user}&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3")).text())[
                           'data']], False
            except:
                return [], True

        assets_cache = (await get_items(username))[0]
        while 1:
            if username == "":
                await asyncio.sleep(0.2)
                continue

            data = await get_items(username)
            if data[1]:
                Visual.betterPrint("[COLOR_RED]Scanner got into a ratelimit, continuing in 1 second.")
                self.ratelimits += 1
                await asyncio.sleep(1)
            if data[0] != assets_cache:
                added = 0
                for _id in data[0]:
                    if _id not in assets_cache:
                        added = _id
                        break

                Visual.betterPrint(f"[COLOR_GREEN]New asset found, adding asset to list. - Found: {added} (USER SCANNER)")
                self.limiteds.append(str(added))
                self.limitednames[str(added)] = "N/A"
                self.finder_added += 1
                assets_cache = data[0]

            await asyncio.sleep(cooldown)

    async def main(self):
        if conf.get("bot enabled", False) is True and conf.get("bot token", "") != "":
            bot = Bot(self)
            asyncio.create_task(bot.start_bot())
        if conf.get("web interface", False) is True:
            await start_site(self)

        asyncio.create_task(self.get_token())
        if self.proxiesOn: asyncio.create_task(self.proxy_token())

        await self.wait()

        while self.cookies[-1][1] == "": await asyncio.sleep(0.01)
        if conf.get("debug", False) is True:
            asyncio.create_task(self.debug_print())
        else:
            asyncio.create_task(self.print_all())

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None),
                                         json_serialize=json.dumps,
                                         trust_env=True,
                                         cookies={".ROBLOSECURITY": self.cookies[-1][0]} if not self.proxiesOn else {},
                                         headers={"x-csrf-token": self.cookies[-1][1]} if not self.proxiesOn else {}) as s:
            if conf.get("user scanner enabled", False) is True and conf.get("scanner user id watching", -1) != -1 and \
                conf.get("scanner user id watching", "Remove me, can be user id or username") != "Remove me, can be user id or username" and \
                conf.get("scanner user id watching", "") != "":
                asyncio.create_task(self.scanner(s))
                Visual.betterPrint("[COLOR_GREEN]Sucessfully started user scanner.", True)

            while 1:
                await self.wait()

                start = time.perf_counter()
                for task in iteration_tasks: asyncio.create_task(task(self))
                if not self.proxiesOn and s.headers["x-csrf-token"] != self.cookies[-1][1]: s.headers["x-csrf-token"] = self.cookies[-1][1]
                self.stats = themeConfig.get("status check", "Checking for onsale limiteds")

                try:
                    data = await self.is_onsale(s, self.limiteds)
                except:
                    Visual.betterPrint("[COLOR_RED]Caught error whilst trying to get the limiteds information.", True)
                    logging.error("ERROR Whilst trying to get limited information: " + traceback.format_exc())
                    self.errors += 1
                    data = False, [], [], False
                self.checks_made += len(self.limiteds)

                if data[0]:
                    for limited in data[1]:
                        Visual.betterPrint(f"[COLOR_CYAN]Buying the {limited['name']} ({limited['id']})[COLOR_WHITE]", True)
                        self.stats = themeConfig.get("status buying", "Buying Limited")
                        self.finder_blacklist.append(str(limited['id']))
                        await self.buy(s, limited)

                self._time = round(time.perf_counter() - start, 3)
                if self._time < self.cooldown and not data[3]:
                    await asyncio.sleep(self.cooldown - self._time)

                self.speed = round(time.perf_counter() - start, 3)


if __name__ == '__main__':
    sniper = UGCSniper()
    try:
        sniper.start()
    except Exception as error:
        for task in error_tasks: task(error)
        logging.error(f"Error log: {traceback.format_exc()}")
        Visual.betterPrint("[COLOR_RED]" + traceback.format_exc())
        Visual.pause()
    finally:
        for task in end_tasks: asyncio.run(task(sniper))
