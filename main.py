import requests as r
from threading import Thread
import os
import uuid
import time

with open("limiteds.txt", "r") as f:
    limiteds = f.read().replace(" ", "").split(",")

with open("cookie.txt", "r") as f:
    cookie = f.read()


user_id = r.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}).json()["id"]
x_token = ""
def get_x_token():
    global x_token

    x_token = r.post("https://auth.roblox.com/v2/logout",
                     cookies={".ROBLOSECURITY": cookie}).headers["x-csrf-token"]
    print("Logged in.")

    while 1:
        # Gets the x_token every 4 minutes.
        x_token = r.post("https://auth.roblox.com/v2/logout",
                         cookies={".ROBLOSECURITY": cookie}).headers["x-csrf-token"]
        time.sleep(248)


def buy(json, itemid, productid):
    print("Buying limited...")

    data = {
        "collectibleItemId": itemid,
        "expectedCurrency": 1,
        "expectedPrice": 0,
        "expectedPurchaserId": user_id,
        "expectedPurchaserType": "User",
        "expectedSellerId": json["creatorTargetId"],
        "expectedSellerType": "User",
        "idempotencyKey": str(uuid.uuid4()),
        "collectibleProductId": productid
    }
    bought = r.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{itemid}/purchase-item", json=data,
        headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()

    if not bought["purchased"]:
        print("Failed buying the limited, trying again..")
        
        try:        
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                      json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                      headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()
        except:
            print("Ratelimit!")
            return

        if info["data"][0]["unitsAvailableForConsumption"] == 0:
            print("Couldn't buy the limited in time. Better luck next time.")
            return

        try:
            productid = r.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                           json={"itemIds": [info["data"][0]["collectibleItemId"]]},
                           headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()[0]["collectibleProductId"]
        except:
            print("Ratelimit Recieved info: ", info)
            return
        
        buy(json, productid, info["data"][0]["collectibleItemId"])
        return

    print(f"Successfully bought the limited! Info: {bought} - {data}")


# Get collectible and product id for all the limiteds.
Thread(target=get_x_token).start()

print("UGC Sniper made by Jeldo#9587\nDiscord server: https://discord.com/invite/3Uvcf8d9aY")
time.sleep(5)
while x_token == "":
    time.sleep(0.01)

# https://apis.roblox.com/marketplace-items/v1/items/details
# https://catalog.roblox.com/v1/catalog/items/details

cooldown = 60/(35/len(limiteds))
while 1:
    start = time.perf_counter()

    for limited in limiteds:
        try:
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                               json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                               headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()['data'][0]
        except KeyError:
            print("Ratelimit waiting for minute to end")
            time.sleep(60-int(datetime.datetime.now().second))
            continue
            
        if info.get("priceStatus", "") != "Off Sale":
            try:
                productid = r.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                       json={"itemIds": [info["collectibleItemId"]]},
                       headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()[0]["collectibleProductId"]
            except:
                print("Ratelimit whilst trying to buy. Recieved info: ", info)
                return

            buy(info, info["collectibleItemId"], productid)

    taken = time.perf_counter()-start
    if taken < cooldown:
        time.sleep(cooldown-taken)

    os.system("cls")
    print("Check done.\n"
          f"Time taken: {round(time.perf_counter()-start, 3)}\n"
          f"Ideal time: {cooldown}")
