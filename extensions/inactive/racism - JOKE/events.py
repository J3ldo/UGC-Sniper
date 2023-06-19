import aiohttp
import rapidjson as json
import os
from themes.required.visual import Visual
from themes.required.sniper import UGCSniper

async def start(sniper: UGCSniper):
    async with aiohttp.ClientSession() as s:
        if json.loads(await (await s.get("https://avatar.roblox.com/v1/avatar", cookies={".ROBLOSECURITY": sniper.cookies[0][0]})).text())["bodyColors"]["headColorId"] in \
            [364, 217, 361, 192]:
            Visual.betterPrint("[COLOR_RED]WARNING - You are black.\n")
            os.system("pause")
            exit(1)

async def iteration(sniper: UGCSniper):
    pass

async def end(sniper: UGCSniper):
    pass

def error(error: Exception):
    pass

def on_load():
    pass

async def buy(sniper: UGCSniper, asset: int, raw_data: dict, sent: dict):
    pass

def ratelimit():
    pass