### credits to sspiky for original, this is heavily modified ###

import time
import json
import requests
from rich import print
from discord_webhook import DiscordWebhook, DiscordEmbed
import subprocess
import aiohttp
import asyncio

webhook_url = ""

with open("cookie.txt", "r") as f:
    cookie = f.read()

def betterPrint(text):
    now = time.strftime('%r')
    print(f"[bold grey53][{now}] [/] {text}")

def get_x_token(cookie):
    return requests.post('https://auth.roblox.com/v2/logout', headers={'cookie': '.ROBLOSECURITY='+ cookie}).headers['x-csrf-token']


def compare(list1, list2):
    added_items = []
    for item in list1:
        if item not in list2:
            added_items.append(item)
    if len(added_items) == 0:
        betterPrint("[aquamarine1]searching...")
        return list2
    else:
        betterPrint(f"[violet]found {len(added_items)} new assets")
        return added_items



def get_item_info(items, cookie):
    details = request_details(items, cookie)
    return extract_data(details)

def request_details(items, cookie):
    headers = {
        'cookie': f'.ROBLOSECURITY={cookie};',
        'x-csrf-token': get_x_token(cookie)
    }
    payload = {'items': items}
    response = requests.post('https://catalog.roblox.com/v1/catalog/items/details',
                             json=payload,
                             headers=headers)
    return response.json()

def extract_data(details):
    return details['data']


def sendWebhook(val):
    print('posting webhook')

    embed = DiscordEmbed(
        title=val['name'],
        url=f"https://www.roblox.com/catalog/{val['id']}",
        color="03b2f8"
        )
    embed.add_embed_field(name='Price', value = val.get('price', 'Offsale'))
    embed.add_embed_field(name='Creator', value = val['creatorName'])
    embed.add_embed_field(name='Stock', value = f"{val['unitsAvailableForConsumption']}")

    msg = DiscordWebhook(url=webhook_url)
    msg.add_embed(embed)
    msg.execute()
        
                        
async def main():
    items = await latest()
    betterPrint(f'loaded {len(items)} items')

    while 1:
        new_items = await latest()
        items = compare(new_items, items)

        if len(items) < 100:
            betterPrint('getting item info')
            item_info = get_item_info(items, cookie)

            for item in item_info:
                sendWebhook(item)
            if item.get('price', 'Offsale') == 0: #adds if lim is free
                with open("limiteds.txt", "w") as file:
                    file.truncate()
                    file.write(f"{item['id']}")
                    input_data = "regular\n" 
                    process = subprocess.Popen(["python", "main.py"], stdin=subprocess.PIPE) #executes main file to buy | change to proxyless.py if using proxyless version
                    process.communicate(input=input_data.encode())
        await asyncio.sleep(3.6)

async def latest():
  try:
    url = 'https://catalog.roblox.com/v2/search/items/details?itemRestrictions=Limited&Category=1&salesTypeFilter=2&SortType=3&Limit=120'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            r = await response.json()
            rData = r['data']
            ids = []
        for item in rData:
            ids.append(item["id"])
    return ids
  except Exception as e:
    print(e)

asyncio.run(main())
