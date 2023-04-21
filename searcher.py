### credits to sspiky for original, this is heavily modified ###

import time
import json
import requests
from rich import print
from discord_webhook import DiscordWebhook, DiscordEmbed
import subprocess
import aiohttp
import asyncio
import json

openjson = open('config.json') 
conf = json.load(openjson)

webhook_url = conf["sniperWebhookURL"]
cookie = conf["cookie"]

snipedIds = []

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
        return added_items



def get_item_info(items, cookie):
    details = request_details(items, cookie)
    return extract_data(details)

def request_details(items, cookie):
    headers = {
        'cookie': f'.ROBLOSECURITY={cookie};',
        'x-csrf-token': get_x_token(cookie)
    }
    #payload = {'items': items}
    payload = {"items": [{"itemType": "Asset", "id": int(items)}]}
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
    iitems = await latest()
    betterPrint(f'loaded {len(iitems)} items')

    while 1:
        new_items = await latest()
        items = compare(new_items, iitems)
        if items is not None and len(items) < 100 and items[0] not in iitems and items[0] not in snipedIds: 
            betterPrint('getting item info')
            item_info = get_item_info(items[0], cookie)
            for item in item_info:
                if conf["webhookEnabled"] == True:
                    sendWebhook(item)
                    print('sent webhook')
                else:
                    print(item)

                snipedIds.append(item['id'])
                if int(item.get('price', 'Offsale')) == 0: #adds if lim is free
                    with open("limiteds.txt", "w") as file:
                        file.truncate()
                        file.write(f"{item['id']}")
                        input_data = "regular\n" 
                        process = subprocess.Popen(["python", "main.py"], stdin=subprocess.PIPE) #executes main file to buy
                        process.communicate(input=input_data.encode())
        await asyncio.sleep(5)


headerss = {
'Content-Type': 'application/json',
'Accept': 'application/json',
        }

json_data = {
'limit': 10,
'cursor': '',
'query': '',
'catalogMode': 'All',
'excludeNonCollectibles': True,
'excludeReleased': False,
'includeNotForSale': False,
'includeForSale': True,
'includeLimitedItems': True,
'sortColumn': 'Updated',
'sortOrder': 'Desc',
'assetTypes': [],
'assetGenres': [],
'creators': [],
'creatorsExclude': [],
'minimumPrice': 0,
'maximumPrice': 999999,
'minimumOwnerCount': 0,
'maximumOwnerCount': 0,
             }


async def latest():
  async with aiohttp.ClientSession() as session:
    async with session.post('https://rblx.trade/api/v2/catalog/asset-search/list', headers=headerss, json=json_data) as response:
      r = await response.json(content_type='application/json')
      rData = r['data']
      ids = []
    for item in rData:
      ids.append(item["id"])
    return ids

asyncio.run(main())
