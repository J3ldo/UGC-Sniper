# Made by:
#   Original code, updates, and onwer: Jeldo#9587
#   Proxy support, fork, better UI: ! max#7948

import requests as r
from threading import Thread
import os
import ctypes
import copy
import uuid
import time
import datetime
from itertools import cycle
import discord_webhook
from discord_webhook import DiscordWebhook, DiscordEmbed
import json

os.system("cls")
ctypes.windll.kernel32.SetConsoleTitleW("J3ldo Sniper")

with open('config.json', "r") as f:
    conf = json.load(f)

with open("./themes/required.json", "r") as f:
    theme_info = json.load(f)

webhook = DiscordWebhook(url=conf["webhook"])  # put a random value in sniperWebhookURL value if you don't want to use a webhook even if webhook is off
s = r.Session()
productid = None
mode_time = False
recent_logs = []


def textToColour(text: str):
    for key in theme_info["colours"]:
        text = text.replace(key, f"\x1b[38;5;{theme_info['colours'][key]}m")

    return text


def betterPrint(content, log=False):
    now = time.strftime('%r')
    if conf["better print"] and log:
        recent_logs.append(textToColour(f"[COLOR_LIGHT_BLUE][{now}] {content}"))
        return

    print(textToColour(f"[COLOR_LIGHT_BLUE][{now}] {content}"))


if conf["auto update"]:
    betterPrint("[COLOR_AQUAMARINE_1A]Checking for potential updates...")
    gitcode = r.get("https://raw.githubusercontent.com/J3ldo/UGC-Sniper/main/main.py").text
    with open("main.py", "r+") as f:
        if f.read() != gitcode:
            betterPrint("[COLOR_AQUAMARINE_1A]Found update! updating code...")
            f.write(gitcode)
            betterPrint("[COLOR_AQUAMARINE_1A]Updated code! restart the sniper to use the newest version")
            os.system("pause")
            exit(0)


# Initialize themes
themeVersion = "1.0.0"

themeLocation = conf["current theme"]
with open(themeLocation+"/config.json", "r") as f:
    themeConfig = json.load(f)
if themeConfig["version"] != themeVersion:
    print(textToColour(f"[COLOR_RED]DEPRECTATION WARNING - Version of the theme is deperecated, theme may not work.\n"
          f"Do you still want to continue? Y/N[COLOR_WHITE]"))
    if input(f"[COLOR_RED]  [>>] [COLOR_WHITE]").lower() == "n":
        exit(1)

ctypes.windll.kernel32.SetConsoleTitleW(themeConfig["title"])

with open(f"{themeLocation}/{themeConfig['logo']}", "r", encoding="unicode_escape") as f: logo = textToColour(f.read())
with open(f"{themeLocation}/{themeConfig['printText']}", "r", encoding="unicode_escape") as f: printText = textToColour(f.read())


limiteds = conf["limiteds"]
if type(limiteds) == str:
    with open(conf["limiteds"], "r") as f:
        contents = f.read()

        if "com" in contents:
            print(textToColour("[COLOR_RED]Invalid id format given, please make sure its only the id not the full link."))
            os.system("pause")
            exit(0)

        if "," in f.read():
            limiteds = contents.replace(" ", "").split(",")
        else:
            limiteds = contents.replace(" ", "").splitlines()

cookies = [[i, ""] for i in conf["cookie"]]
if type(conf["cookie"]) == str:
    with open(conf["cookie"], "r") as f:
        cookies = [[i, ""] for i in f.read().replace(";", "").splitlines()]

with open(conf["proxies"], "r") as f:
    proxies = f.read().splitlines()
    proxiesOn = bool(proxies)
    proxy = "N/A"

    if proxiesOn:
        proxy_pool = cycle(proxies)
        proxy = next(proxy_pool)

try:
    info = r.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookies[0][0]}).json()

    user_id = info["id"]
    user_name = info["name"]
    display_name = info["displayName"]
except KeyError:
    betterPrint("[COLOR_RED]Invalid Cookie, please check that you have no newlines, spaces or commas at the end or in the file.")
    os.system("pause")
    exit(1)

print(textToColour(f"[COLOR_LIGHT_BLUE]UGC-Sniper made by: Jeldo#9587 (J3ldo) and ! max#7948 (maxhithere)\n"
      f"[COLOR_LIGHT_BLUE]Discord server: https://discord.com/invite/3Uvcf8d9aY)"))
time.sleep(3)

print(textToColour(f"[COLOR_LIGHT_BLUE]Logged in as {user_name}"))

x_token = ""
bought = 0
proxy_changed = 0
ratelimits = 0
checks_made = 0
cooldown = 0
_time = 0
speed = 0
minutes = int(conf["time wait minutes"])
stats = textToColour("[COLOR_GREEN]Sniping")

soldout = False
switchcookie = False
currentCookie = 0
boughtsession = 0

modes = ["regular", "afk", "time"]

mode = conf.get("mode", "")
if conf.get("mode", "") not in modes:
    print(textToColour(f"[COLOR_BLUE][>>] Choose mode: {', '.join(modes)}"))
    mode = input(textToColour(f"[COLOR_BLUE]   [>>] "))
if mode not in modes:
    betterPrint("[COLOR_RED]Invalid Mode Selected")
    os.system("pause")
    exit(1)

if mode == "regular":
    try:
        cooldown = 60 / (80 / len(limiteds))
    except ZeroDivisionError:
        betterPrint("[COLOR_RED]No limiteds added, please add a limited for the sniper to work.")
        os.system("pause")
        exit(1)

    cooldown = conf["custom afk cooldown"] if conf["custom regular cooldown"] >= 0 else cooldown

elif mode == "afk":
    try:
        cooldown = 60 / (50 / len(limiteds))
    except ZeroDivisionError:
        betterPrint("[COLOR_RED]No limiteds added, please add a limited for the sniper to work.")
        os.system("pause")
        exit(1)
    cooldown = conf["custom afk cooldown"] if conf["custom afk cooldown"] >= 0 else cooldown

else:
    mode_time = True
    if minutes < 0:
        print(textToColour("[COLOR_LIGHT_BLUE][>>] Enter number of minutes untill ugc releases: "))
        minutes = int(input(textToColour("[COLOR_LIGHT_BLUE]   [>>] ")))
    betterPrint(f"[COLOR_VIOLET][*] Sniper will run for {minutes} minutes / {minutes*60} seconds before speed sniping")
    time.sleep(3)

    cooldown = conf["custom time cooldown"]
    if len(limiteds) == 0:
        betterPrint("[COLOR_RED]No limiteds added, please add a limited for the sniper to work.")
        os.system("pause")
        exit(1)

def get_x_token():
    global x_token
    x_token = r.post("https://auth.roblox.com/v2/logout",
                     cookies={".ROBLOSECURITY": cookies[0][0]}).headers["x-csrf-token"]

    while 1:
        for idx, _ in enumerate(cookies):
            cookies[idx][1] = r.post("https://auth.roblox.com/v2/logout",
                             cookies={".ROBLOSECURITY": cookies[idx][0]}).headers["x-csrf-token"]
            if idx == 0:
                x_token = cookies[idx][1]

            time.sleep(300/len(cookies))


def textToVar(text: str):
    custom_vars = {
        "[username]": user_name,
        "[displayName]": display_name,
        "[userId]": user_id,

        "[proxiesEnabled]": proxiesOn,
        "[proxyAmount]": len(proxies),
        "[currentProxy]": proxy,
        "[changedProxies]": proxy_changed,
        "[ratelimits]": ratelimits,

        "[time]": _time,
        "[limitedsAmount]": len(limiteds),
        "[limiteds]": limiteds,
        "[speed]": speed,
        "[status]": stats,
        "[priceChecks]": checks_made,
        "[bought]": bought,

        "[x-csrf]": x_token,
        "[cooldown]": cooldown,
    }

    for key in custom_vars:
        text = text.replace(key, str(custom_vars[key]))

    return text

def printall():
    global recent_logs

    iteration = 0
    while 1:
        if iteration > 3:
            iteration = 0
            recent_logs = []

        os.system("cls")
        print(logo+textToVar(printText)+"\n\nLogs:\n"+"\n".join(i for i in recent_logs))

        time.sleep(conf["print update cooldown"])
        iteration += 1

def getStock():
    try:
        info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                            headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookies[0][0]},
                            proxies={'http': "http://" + proxy} if proxiesOn else {})
    except:
        betterPrint('[COLOR_RED]ERROR CAUGHT WHILST TRYING TO GET THE STOCK')
        return 1

    try:
        left = info.json()["data"][0]["unitsAvailableForConsumption"]
    except:
        betterPrint(f"[COLOR_RED]Failed getting stock. Full log: {info.text} - {info.reason}")
        left = 1

    return left


def rawbuy(data, other, cookie):
    global soldout, switchcookie, proxy, bought, boughtsession, proxy_changed

    try:
        _bought = r.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{other['itemid']}/purchase-item",
                              json=data, headers={"x-csrf-token": cookie[1]}, cookies={".ROBLOSECURITY": cookie[0]},
                              proxies={'http': "http://" + proxy} if proxiesOn and conf["purchase proxy"] else {})
    except:
        betterPrint('[COLOR_RED]ERROR CAUGHT WHILST TRYING TO PURHCASE ITEM')
        return

    if _bought.reason == "Too Many Requests":
        if proxiesOn:
            proxy = next(proxy_pool)  # switch proxy
            proxy_changed += 1
            return

        betterPrint(f"[COLOR_RED]Ratelimit for buying limited.")
        time.sleep(1)
        return

    try:
        _bought = _bought.json()
    except:
        betterPrint(f"[COLOR_YELLOW]Json decoder error whilst trying to buy item. - Reason {_bought.status_code}-{_bought.reason}")
        return


    if _bought['purchaseResult'] == 'Flooded':
        betterPrint(f"[COLOR_GREEN]Bought maximum amount of items on account. Switching cookies")
        switchcookie = True

    if _bought['errorMessage'] == 'QuantityExhausted':
        betterPrint(f"[COLOR_RED]All items sold out.")
        soldout = True

    if not _bought["purchased"]:
        betterPrint(f"[COLOR_RED]Failed buying limited, trying again.. Info: {_bought} - {data}")

    if _bought["purchased"]:
        betterPrint(f"[COLOR_AQUAMARINE_1A]Successfully bought limited! Info: {_bought} - {data}")
        bought += 1
        boughtsession += 1

        if conf["webhook enabled"] is True:

            embed = DiscordEmbed(title='Purchased Limited', description='You successfully sniped a limited!',
                                 color='03b2f8')
            embed.add_embed_field(name=f'Item', value=f'[{other["itemName"]}](https://www.roblox.com/catalog/{other["assetid"]})')
            embed.add_embed_field(name=f'Stock', value=f'{other["left"]}')
            embed.add_embed_field(name=f'Recieved', value=f'{_bought}')
            webhook.add_embed(embed)
            webhook.execute()


def buy(json, itemid, productid, itemName, itemQuan, assetid):
    global bought, boughtsession, switchcookie, currentCookie
    betterPrint("[COLOR_AQUAMARINE_1A]Buying Limited")

    data = {
        "collectibleItemId": itemid,
        "expectedCurrency": 1,
        "expectedPrice": 0,
        "expectedPurchaserId": user_id,
        "expectedPurchaserType": "User",
        "expectedSellerId": json["creatorTargetId"],
        "expectedSellerType": "User",
        "idempotencyKey": "random uuid4 string that will be your key or smthn",
        "collectibleProductId": productid
    }

    left = itemQuan
    other = {
        "itemid": itemid,
        "itemName": itemName,
        "assetid": assetid,
        "left": left
    }

    for cookie in cookies:
        while 1:
            threads = []
            for i in range(8):
                data["idempotencyKey"] = str(uuid.uuid4())

                threads.append(Thread(target=rawbuy, args=(copy.copy(data), other, cookie,)))
                threads[i].start()

            left = getStock()

            for thread in threads:
                thread.join()

            if left == 0 or soldout:
                break

            if boughtsession >= 4 or switchcookie:
                switchcookie = False
                boughtsession = 0

        if left == 0 or soldout:
            betterPrint("[COLOR_RED]Couldn't buy the limited in time")
            break

    boughtsession = 0
    switchcookie = False


Thread(target=get_x_token).start()
betterPrint("[COLOR_VIOLET][*] Starting Sniper")

while x_token == "":
    time.sleep(0.01)

if mode_time is True:
    betterPrint(
        "[COLOR_AQUAMARINE_1A]You picked time. Feel the essence of the sniper and the power of the limiteds. The great fortunes you can make, just by waiting..")
    betterPrint(f"[COLOR_PINK_1][*] You have {minutes} minutes left.")
    for i in range(minutes):
        time.sleep(60)
        betterPrint(f"[COLOR_PINK_1][*] You have {minutes - (i + 1)} minutes left.")

    betterPrint(f"[COLOR_PINK_1][*] Time ended. Starting spam sniper.")

Thread(target=printall).start()
while 1:
    start = time.perf_counter()

    for limited in limiteds:
        try:
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                          json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                          headers={"x-csrf-token": x_token},
                          cookies={".ROBLOSECURITY": cookies[0][0]},
                          proxies={'http': "http://" + proxy} if proxiesOn else {}).json()["data"][0]
        except:
            if proxiesOn:
                proxy = next(proxy_pool)  # switch proxy
                proxy_changed += 1

                time.sleep(conf["proxy ratelimit cooldown"])
                continue

            betterPrint(f"[COLOR_RED]Ratelimit for seeing if item in on sale.")
            ratelimits += 1
            time.sleep(conf["ratelimit cooldown"])
            continue

        if info.get("collectibleItemId") is not None:
            productid = r.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                               json={"itemIds": [info["collectibleItemId"]]},
                               headers={"x-csrf-token": x_token},
                               cookies={".ROBLOSECURITY": cookies[0][0]},
                               proxies={'http': "http://" + proxy} if proxiesOn else {})

            try:

                productid = productid.json()[0]["collectibleProductId"]
            except:
                betterPrint(
                    f"[COLOR_RED]Something went wrong whilst getting the product id Logs - {productid.text} - {productid.reason}")
                continue
            buy(info, info["collectibleItemId"], productid, info["name"], info["totalQuantity"], info["id"])

    taken = time.perf_counter() - start
    _time = taken
    stats = textToColour(f"[COLOR_GREEN]Running")

    if taken < cooldown:
        time.sleep(cooldown-taken)

    checks_made += len(limiteds)
    speed = round(taken, 2)
