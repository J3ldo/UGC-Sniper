from quart import Quart, render_template
import quart
import logging
import asyncio
import json
import aiohttp
import os

from themes.required.visual import Visual
from __main__ import all_logs, conf

app = Quart(__name__)

sniper = None
fact = "N/A"


class Commands:
    @staticmethod
    def help(text, text_split, args):
        logging.info("Help command executed")

        Visual.add_log(
            f"Help command: <br>"
            f"<indent><b>>help</b> - <b>Shows this command</b></indent><br>"
            f"<indent><b>>add</b>  - <b>Adds a limited</b></indent><br>"
            f"<indent><b>>view</b> - <b>Lists all the limiteds added</b></indent><br>"
            f"<indent><b>>remove</b> - <b>Removes an id from the sniper</b></indent><br>"
            f"<indent><b>>clear</b> - <b>Clears every limited.</b></indent><br>"
            f"<indent><b>>pause</b> - <b>Pauses the sniper.</b></indent><br>"
            f"<indent><b>>unpause</b> - <b>Unpauses the sniper.</b></indent><br>"
            f"<indent><b>>cooldown</b> - <b>Sets the cooldown of the sniper</b></indent><br>"
        )

    @staticmethod
    def add(text, text_split, args):
        logging.info(f"Add command executed with the following limiteds: {args}")
        ids = [_id.replace(" ", "") for _id in args]

        sniper.limiteds += ids
        for _id in ids: sniper.limitednames[str(_id)] = "N/A"
        ids = [f"> <b>{_id}</b>" for _id in ids]

        Visual.add_log(
            f"Successfully added the following limited(s): <br>"
            + ''.join([f"<indent>{_id}</indent><br>" for _id in ids])  # Good code (Im lazy)
        )

    @staticmethod
    def view(text, text_split, args):
        logging.info(f"View command executed")
        ids = "<br>".join([f"<indnet>> <b>{_id}</b> - <b>{sniper.limitednames.get(str(_id), 'N/A')}</b></indent>" for _id in sniper.limiteds])

        Visual.add_log(
            "All limited(s) currently added to the sniper: <br>"
            f"{ids}"
        )

    @staticmethod
    def remove(text, text_split, args):
        logging.info(f"Remove command executed for the following ids: {args}")
        for _id in args:
            if _id not in sniper.limiteds:
                ids = "<br>".join([f"<indent>> <b>{_id}</b></indent>" for _id in sniper.limiteds])
                Visual.add_log(
                    "ERROR - Id not in added limiteds<br><br>"
                    f"Id: <b>{_id}</b><br>"
                    "Added ids: <br>"
                    f"{ids}",
                )
                return
            sniper.limiteds.remove(_id)

        removed = '<br>'.join([f'<indent>> <b>{_id}</b></indent>' for _id in args])
        lims = "<br>".join([f"<indent>> <b>{_id}</b></indent>" for _id in sniper.limiteds])
        Visual.add_log(
            "Successfully removed the following ids.<br>"
            "Removed ids: <br>"
            f"{removed}"
            "<br><br>Ids currently searching for: <br>"
            f"{lims}",
        )

    @staticmethod
    def cooldown(text, text_split, args):
        try: sniper.cooldown = float(args[0])
        except ValueError:
            Visual.add_log(f"ERROR - No valid cooldown parsed")
            return

        Visual.betterPrint(f"[COLOR_GREEN]Successfully set the cooldown to: {sniper.cooldown} seconds")

    @staticmethod
    def clear(text, text_split, args):
        sniper.limiteds = []
        sniper.limitednames = {}

        Visual.add_log(
            "Successfully cleared every limited.<br>"
            "To add a limited remember use the add command.<br><br>"
            "<b>THIS ACTION CAN BE UNDONE BY RESTARTING THE SNIPER</b>",
        )

    @staticmethod
    def pause(text, text_split, args):
        try: sniper.minutes = int(args[0])
        except:
            Visual.add_log("<b>No minutes or an invalid input has been given. Please put in like so: >pause 10</b>")
            return
        Visual.add_log(
            "Successfully paused the sniper.<br>"
        )

    @staticmethod
    def unpause(text, text_split, args):
        sniper.minutes = 0
        Visual.add_log(
            "Successfully unpaused the sniper.<br>"
        )

    @staticmethod
    def not_found(text, text_split, args):
        Visual.betterPrint(f"[COLOR_RED]Command not found: {text}")


commands = {
    ">help": Commands.help,
    ">add": Commands.add,
    ">view": Commands.view,
    ">remove": Commands.remove,
    ">cooldown": Commands.cooldown,
    ">clear": Commands.clear,
    ">pause": Commands.pause,
    ">unpause": Commands.unpause
}
def run_command(text, text_split, command, args):
    commands.get(command, Commands.not_found)(text, text_split, args)

@app.get('/')
async def index():
    return await render_template("index.html", sniper=sniper, fact=fact)


@app.get("/get-console")
async def getconsole():
    return quart.jsonify(all_logs)

@app.get("/get-stats")
async def getstats():
    return (f"Status: <b>{sniper.stats}</b><br>"
            f"Mode: <b>{sniper.mode}</b><br><br>"
            f"Time: <b>{sniper._time}</b><br>"
            f"<indent>--> Speed: <b>{sniper.speed}</b></indent><br><br>"
            f"Price checks: <b>{sniper.checks_made}</b><br>"
            f"<indent>--> Free bought: <b>{sniper.bought}</b></indent><br>"
            f"<indent>--> Bought paid: <b>{sniper.boughtpaid}</b></indent>")


@app.post("/execute")
async def execute_command():
    if (await quart.request.json).get("text") is None:
        return {"message": "No text param given"}, 400

    text = (await quart.request.json)["text"]
    text_split = text.split()
    if text == "":
        Visual.betterPrint(f"[COLOR_RED]No text given.")
        return

    if len(text_split) == 0 and text[0] != ">":
        Visual.betterPrint(f"{text} - Invalid command given type >help for help")

    command = text_split[0]
    args = []
    if len(text_split) >= 2:
        args = text_split[1].split(",")

    result = ""
    Visual.betterPrint(f"[COMMAND EXECUTED] {text} - {result} ({command}, {','.join(args)})")
    run_command(text, text_split, command, args)

    return {"message": "Success"}, 200

@app.get("/add-ids")
async def add_id():
    _id = quart.request.args.get("ids", "")
    if _id == "":
        return {"message": "No id param given"}, 400

    Commands.add(None, None, _id.replace(" ", "").split(","))
    return {"message": "Success"}, 200

@app.get("/set-cooldown")
async def set_cooldown():
    cooldown = quart.request.args.get("cooldown", 0)
    if cooldown == 0:
        return {"message": "No id param given"}, 400

    Commands.cooldown(None, None, [cooldown])
    return {"message": "Success"}, 200

@app.get("/get-logs")
async def get_logs():
    return await quart.send_file("./logs/" + os.listdir("logs")[-1], as_attachment=True)

async def get_cat_fact():
    global fact

    async with aiohttp.ClientSession() as s:
        while 1:
            try: fact = json.loads(await (await s.get("https://catfact.ninja/fact")).text())["fact"]
            except: await asyncio.sleep(10)
            await asyncio.sleep(10)


async def start_site(_sniper):
    import socket
    global sniper
    sniper = _sniper

    Visual.betterPrint("[COLOR_GREEN]Successfully started the web interface.")
    Visual.betterPrint(f"[COLOR_GREEN]Hosting web interface on: {socket.gethostbyname(socket.gethostname())}/127.0.0.1")
    asyncio.create_task(get_cat_fact())
    asyncio.create_task(app.run_task("0.0.0.0", 80, debug=True))
    logging.getLogger('quart.serving').setLevel(logging.ERROR)