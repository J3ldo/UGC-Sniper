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


webhook = DiscordWebhook(url='')
s = r.Session()


with open("limiteds.txt", "r") as f:
    limiteds = f.read().replace(" ", "").split(",")

with open("cookie.txt", "r") as f:
    cookie = f.read()

with open("proxies.txt", "r") as f:
    proxies = f.read().splitlines()
    proxy_pool = cycle(proxies)
    proxy = next(proxy_pool)

    try:
        user_id = r.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+proxy}).json()["id"]
    except:
        print(fore.RED + "Invalid Cookie")
x_token = ""
x_lims = 0
x_proxy = 0
stats = f"{fore.GREEN}Sniping"

def run(speed, color, proxy):
    os.system("cls")
    print(
        f"{fore.WHITE}[Time: {fore.YELLOW}{round(time.perf_counter()-start, 3)}{fore.WHITE}]\n  → {fore.WHITE}[Speed: {fore.YELLOW}{speed}{fore.WHITE}]\n{fore.WHITE}[Bought UGCs: {fore.GREEN}{x_lims}{fore.WHITE}]\n{fore.WHITE}[Changed Proxies: {fore.RED}{x_proxy}{fore.WHITE}]\n  → {fore.WHITE}[Current Proxy: {fore.YELLOW}{proxy}{fore.WHITE}]\n{fore.WHITE}[Status: {fore.YELLOW}{stats}{fore.WHITE}]"
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


def buy(json, itemid, productid, prox, session):
    print(fore.GREEN + "BUYING LIMITED: " + productid)
    

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
            bought = session.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{itemid}/purchase-item", json=data,
                headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+prox})

            if bought.reason == "Too Many Requests":
              
                proxy = next(proxy_pool) # switch proxy
                time.sleep(0.5)
                usedProxies(proxy)
                continue

            try:
                bought = bought.json()
            except:
                print(bought.reason)
                print(fore.YELLOW +"Json decoder error whilst trying to buy item.")
                continue

            if not bought["purchased"]:
                print(fore.RED + f"Failed buying the limited, trying again.. Info: {bought} - {data}")
            else:
                print(fore.GREEN + f"Successfully bought the limited! Info: {bought} - {data}")
                embed = DiscordEmbed(title='Purchased Limited', description=f'{bought} - {data}', color='00FF00') 
                webhook.add_embed(embed)
                webhook.execute()
                boughtLim()
            try:
                info = session.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                            headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+prox})
            except:
                print(fore.RED + 'ERROR CAUGHT')
            try:
                left = info.json()["data"][0]["unitsAvailableForConsumption"] 
            except:
                print(fore.RED + f"Failed getting stock. Full log: {info.text} - {info.reason}")
                left = 0

            if left == 0:
                print(fore.RED + "Couldn't buy the limited in time")
                return
        except:
            print(fore.RED + 'ERROR CAUGHT')


# Get collectible and product id for all the limiteds.
Thread(target=get_x_token).start()

print("Starting Sniper")
while x_token == "":
    time.sleep(0.01)

cooldown = 60/(39/len(limiteds))
while 1:
    start = time.perf_counter()

    for limited in limiteds:
        try:
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                           json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                           headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+proxy}).json()["data"][0]
        except:
             
              proxy = next(proxy_pool) # switch proxy
              usedProxies(proxy)
              time.sleep(6.9)
              continue

        if info.get("priceStatus", "") != "Off Sale" and info.get("collectibleItemId") is not None:
            productid = r.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                   json={"itemIds": [info["collectibleItemId"]]},
                   headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}, proxies={'http':"http://"+proxy})

            try:
                productid = productid.json()[0]["collectibleProductId"]
            except:
                print(fore.RED + f"Something went wrong whilst getting the product id Logs - {productid.text} - {productid.reason}")
                continue

            buy(info, info["collectibleItemId"], productid, proxy, s)

    taken = time.perf_counter()-start
    stats = f"{fore.GREEN}Running"
    if taken < cooldown:
        settle = cooldown-taken-0.7 # REMOVE -0.7 IF YOU WANT SLOWER RATES 1-1.5 BUT NO RATELIMITS
        if settle < 0:
            settle = 0.3
        time.sleep(settle) # better wait time
    run(str(taken), fore.GREEN, proxy)
