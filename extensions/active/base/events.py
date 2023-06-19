from themes.required.sniper import UGCSniper

async def start(sniper: UGCSniper):
    pass

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