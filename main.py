import requests as r
from threading import Thread
import os
import uuid
import time
import datetime
from itertools import cycle
import colored
from colored import fore, back, style
import discord_webhook
from discord_webhook import DiscordWebhook, DiscordEmbed
from rich import print as rprint
import json


openjson = open('config.json') 
conf = json.load(openjson)
 
webhook = DiscordWebhook(url=conf["sniperWebhookURL"]) # put a random value in sniperWebhookURL value if you don't want to use a webhook even if webhook is off
s = r.Session()
productid = None
mode_time = False

def betterPrint(content):
    now = time.strftime('%r')
    rprint(f"[bold grey53][{now}] [/] {content}")

betterPrint("[aquamarine1]checking for potential updates...")
gitcode = r.get("https://raw.githubusercontent.com/maxhithere/UGC-Sniper/main/main.py").text
with open("main.py", "r") as f:
    if f.read() != gitcode:
        betterPrint("[aquamarine1]found update! updating code...")
        with open("main.py", "w") as f:
            f.write(gitcode)
            betterPrint("[aquamarine1]updated code! restart the sniper to use the newest version")
            exit(0)
 
with open("limiteds.txt", "r") as f:
    limiteds = f.read().replace(" ", "").split(",")
 
    cookie = conf["cookie"]
 
with open("proxies.txt", "r") as f:
    proxies = f.read().splitlines()
    proxy_pool = cycle(proxies)
    proxy = next(proxy_pool)

try:
    user_id = r.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+proxy}).json()["id"]
except:
    betterPrint("[red3]Invalid Cookie")
 
x_token = ""
x_lims = 0
x_proxy = 0
stats = f"{fore.GREEN}Sniping"
 
modes = ["regular", "afk", "time"]
print(fore.LIGHT_BLUE + f"[>>] Choose mode: {', '.join(modes)}")
mode = input(fore.BLUE + f"   [>>] ")
if mode not in modes:
    betterPrint("[red3]Invalid Mode Selected")
    exit()
 
if mode == "regular":
    settle = 0.5
elif mode == "afk":
    settle = 1.3
else:
    mode_time = True
    print(fore.LIGHT_BLUE + "[>>] Enter number of minutes untill ugc releases: ")
    global minutes
    minutes = int(input(fore.BLUE + "   [>>] "))
    betterPrint(f"[violet][*] Sniper will run for {minutes} minutes before speed sniping")
    time.sleep(3)
    settle = 0.5
 
def run(speed, color, proxy):
    os.system("cls")
    print(
        f"{fore.WHITE}[Time: {fore.YELLOW}{round(time.perf_counter()-start, 3)}{fore.WHITE}]\n  --> {fore.WHITE}[Speed: {fore.YELLOW}{speed}{fore.WHITE}]\n{fore.WHITE}[Bought UGCs: {fore.GREEN}{x_lims}{fore.WHITE}]\n{fore.WHITE}[Changed Proxies: {fore.RED}{x_proxy}{fore.WHITE}]\n  --> {fore.WHITE}[Current Proxy: {fore.YELLOW}{proxy}{fore.WHITE}]\n{fore.WHITE}[Status: {fore.YELLOW}{stats}{fore.WHITE}]"
    )
 
def statusCMD(got):
    global stats
    stats = got
 
def usedProxies(proxy):
    global x_proxy
    x_proxy = x_proxy + 1
    limitedProxy = proxy
    statusCMD(f"{fore.YELLOW}Changing Proxy")
    run("N/A", fore.YELLOW, limitedProxy)
 
def boughtLim():
    global x_lims
    x_lims = x_lims + 1
 
def get_x_token():
    global x_token
    x_token = r.post("https://auth.roblox.com/v2/logout",
                     cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+proxy}).headers["x-csrf-token"]
 
    while 1:
        x_token = r.post("https://auth.roblox.com/v2/logout",
                         cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+proxy}).headers["x-csrf-token"]
        time.sleep(248)    



def buy(json, itemid, productid, prox, session, itemName, itemQuan, itemID):
    betterPrint("[aquamarine1]Buying Limited")

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

    while 1:
        try:
            data["idempotencyKey"] = str(uuid.uuid4())
            bought = session.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{itemid}/purchase-item", json=data, headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+prox})
        except:
            betterPrint('[red3]ERROR CAUGHT')
            continue

        if bought.reason == "Too Many Requests":
            proxy = next(proxy_pool) # switch proxy
            time.sleep(0.5)
            usedProxies(proxy)
            continue

        try:
            bought = bought.json()
        except:
            print(bought.reason)
            betterPrint("[yellow]Json decoder error whilst trying to buy item.")
            continue
            
        if bought['errorMessage'] == 'QuantityExhausted':
            betterPrint(f"[red3]Too many items being bought at once. Roblox API is heavy ratelimiting.")

        if not bought["purchased"]:
            betterPrint(f"[red3]Failed buying limited, trying again.. Info: {bought} - {data}")
                        
        if bought["purchased"]:
            betterPrint(f"[aquamarine1]Successfully bought limited! Info: {bought} - {data}")
        if conf["webhookEnabled"] == True:
            embed = DiscordEmbed(title='Purchased Limited', description='You successfully sniped a limited!', color='03b2f8')
            embed.add_embed_field(name=f'Item', value=f'[{itemName}](https://www.roblox.com/catalog/{itemID})')
            embed.add_embed_field(name=f'Stock', value=f'{itemQuan}')
            embed.add_embed_field(name=f'Recieved', value=f'{x_lims + 1}')
            webhook.add_embed(embed)
            webhook.execute()
            boughtLim()
            break

        try:
            info = session.post("https://catalog.roblox.com/v1/catalog/items/details",
                json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+prox})
        except:
            betterPrint('[red3]ERROR CAUGHT')

        try:
            left = info.json()["data"][0]["unitsAvailableForConsumption"]
        except:
            betterPrint(f"[red3]Failed getting stock. Full log: {info.text} - {info.reason}")
            left = 0

        if left == 0:
            betterPrint("[red3]Couldn't buy the limited in time")
            break

 
Thread(target=get_x_token).start()
betterPrint("[violet][*] Starting Sniper")
 
while x_token == "":
    time.sleep(0.01)
 
cooldown = 60 / (39 / len(limiteds))
 
while 1:
    start = time.perf_counter()
 
    for limited in limiteds:
        try:
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                           json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                           headers={"x-csrf-token": x_token},
                           cookies={".ROBLOSECURITY": cookie},
                           proxies={'http': "http://" + proxy}).json()["data"][0]
        except:
            proxy = next(proxy_pool)
            usedProxies(proxy)
            betterPrint("[yellow1]cookie ratelimited, sleeping for 5 sec and switching proxy.")
            time.sleep(5)
 
        if info.get("priceStatus", "") != "Off Sale" and info.get("collectibleItemId") is not None:
            productid = r.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                               json={"itemIds": [info["collectibleItemId"]]},
                               headers={"x-csrf-token": x_token},
                               cookies={".ROBLOSECURITY": cookie},
                               proxies={'http': "http://" + proxy})
 
            try:
                
                productid = productid.json()[0]["collectibleProductId"]
            except:
                    betterPrint(f"[red3]Something went wrong whilst getting the product id Logs - {productid.text} - {productid.reason}")
                    continue
            buy(info, info["collectibleItemId"], productid, proxy, s, info["name"], info["totalQuantity"], info["id"])


        if mode_time == True:
                betterPrint("[aquamarine1]You picked time. Feel the essence of the sniper and the power of the limiteds. The great fortunes you can make, just by waiting..")
                betterPrint(f"[pink1][*] You have {minutes} minutes left.")
                time.sleep(minutes * 60)
                betterPrint(f"[pink1][*] Time ended. Starting spam sniper.")
                mode_time = False
                    



    taken = time.perf_counter()-start
    stats = f"{fore.GREEN}Running"
    time.sleep(settle)
    run(str(taken), fore.GREEN, proxy)
