import discord
from discord.ext import commands
import logging
import os
import time
import json
import aiohttp
import sys

extensions_path = os.path.dirname(os.path.abspath(__file__))
themes_path = os.path.join(extensions_path, '..', 'themes')
sys.path.insert(0, themes_path)
from themes.required.sniper import UGCSniper 
from themes.required.visual import Visual

with open('config.json', "r") as f:
    conf = json.load(f)


class Bot(commands.Bot):
    def __init__(self, sniper: UGCSniper):
        self.sniper = sniper
        self.prefix = conf.get("preifx", ">")

        super().__init__(command_prefix=self.prefix, intents=discord.Intents.all())
        self.init_commands()

    def init_commands(self):
        @self.command()
        async def ping(ctx: commands.Context):
            logging.info("Ping command executed")
            await ctx.send("Pong! :ping_pong:\n"
                           f"Latency: {round(self.latency*1000)}ms")

        @self.command()
        async def stats(ctx: commands.Context):
            logging.info("Stats command executed")

            embed = discord.Embed(title="Stats for UGC Sniper",
                                  colour=discord.Colour.blue())
            embed.add_field(name="Basic info",
                            value=f"Status: **{self.sniper.stats}**\n"
                                  f"Mode: **{self.sniper.mode}**\n\n"
                                  f"Time: **{self.sniper._time}**\n"
                                  f">    --> Speed: **{self.sniper.speed}**\n\n"
                                  f"Price checks: **{self.sniper.checks_made}**\n"
                                  f">    --> Free bought: **{self.sniper.bought}**\n"
                                  f">    --> Bought paid: **{self.sniper.boughtpaid}**",)

            embed.add_field(name="Added ids", value="\n".join([f"> **{_id}** - **{self.sniper.limitednames[_id]}**" for _id in self.sniper.limiteds]), inline=True)
            embed.set_footer(text=f"Requested by: {ctx.author.display_name}", icon_url=ctx.author.display_avatar)

            await ctx.send(embed=embed)

        @self.command("add")
        async def add_limiteds(ctx: commands.Context, *, ids:str):
            logging.info(f"Add command executed with the following limiteds: {ids}")
            ids = ids.replace(" ", "").split(",")

            self.sniper.limiteds += ids
            for _id in ids: self.sniper.limitednames[_id] = "N/A"
            ids = [f"> **{_id}**" for _id in ids]

            await ctx.send(embed=discord.Embed(
                title="Successfully added ids",
                description="Successfully added the following ids the the sniper: \n"
                            "\n".join(ids),
                colour=discord.Colour.green()
            ))

        @self.command("view")
        async def view_limiteds(ctx: commands.Context):
            logging.info("View command executed")
            ids = "\n".join([f"> **{_id}** - **{self.sniper.limitednames[_id]}**" for _id in self.sniper.limiteds])

            await ctx.send(embed=discord.Embed(
                title="Successfully listed all ids",
                description="All ids currently added to the sniper: \n"
                            f"{ids}",
                colour=discord.Colour.green()
            ))

        @self.command("remove")
        async def remove_ids(ctx: commands.Context, *, ids: str):
            logging.info(f"Remove command executed for the following ids: {ids}")
            ids = ids.replace(" ", "").split(",")

            for _id in ids:
                if _id not in self.sniper.limiteds:
                    ids = "\n".join([f"> **{_id}**" for _id in self.sniper.limiteds])
                    await ctx.send(embed=discord.Embed(
                        title="ERROR - Id not in added limiteds",
                        description="The following id is not in the added ids\n\n"
                                    f"Id: **{_id}**\n"
                                    "Added ids: \n"
                                    f"{ids}",
                        colour=discord.Colour.red()
                    ))
                    return
                self.sniper.limiteds.remove(_id)

            removed = '\n'.join([f'> **{_id}**' for _id in ids])
            lims = "\n".join([f"> **{_id}**" for _id in self.sniper.limiteds])
            await ctx.send(embed=discord.Embed(
                title="Successfully removed the following ids.",
                description="Successfully removed all the specified ids.\n"
                            "Removed ids: \n"
                            f"{removed}"
                            "\n\nIds currently searching for: \n"
                            f"{lims}",
                colour=discord.Colour.green()
            ))

        @self.command("kill")
        async def kill_bot(ctx: commands.Context):
            logging.warning("Kill command exectuted")
            await ctx.send("Killing bot.")
            exit(1)

        @self.command("logs")
        async def dump_logs(ctx: commands.Context):
            logging.info("Logs command exectuted")
            await ctx.send(file=discord.File("./logs/"+os.listdir("logs")[-1]))

        @self.command("catfact")
        async def catfact(ctx: commands.Context):
            async with aiohttp.ClientSession() as s:
                fact = json.loads(await (await s.get("https://catfact.ninja/fact")).text())["fact"]
            await ctx.send(embed=discord.Embed(
                title="Did you know that...",
                description=f"```fix\n{fact}```",
                colour=discord.Colour.blue()
            ))

        @self.command("mode")
        async def mode_info(ctx: commands.Context):
            timestamp = f"<t:{round(time.time()+self.sniper.minutes*60)}:R>" if self.sniper.mode_time else "**N/A**"
            added = "\n".join([f"> **{_id}** - **{self.sniper.limitednames[_id]}**" for _id in self.sniper.limiteds])
            await ctx.send(embed=discord.Embed(
                title="Showing mode info",
                description=f"Mode: **{self.sniper.mode}**\n"
                            f"Starting in: {timestamp}\n\n"
                            f"Cooldown: **{self.sniper.cooldown}** seconds\n"
                            f"Added limiteds: \n"
                            f"{added}",
                colour=discord.Colour.green()
            ))

        self.remove_command("help")
        @self.command("help")
        async def command_help(ctx: commands.Context):
            await ctx.send(embed=discord.Embed(
                title="Help command",
                description=f"**{self.prefix}help** - **Shows this command**\n"
                            f"**{self.prefix}ping** - **Pings the bot to see if its online**\n"
                            f"**{self.prefix}stats** - **Show the stats of the sniper.**\n"
                            f"**{self.prefix}mode** - **Shows info about the current mode.**\n"
                            f"**{self.prefix}view** - **Lists all the ids added to the sniper**\n"
                            f"**{self.prefix}add** - **Add one or multiple ids to the sniper (Seperate with commas)**\n"
                            f"**{self.prefix}remove** - **Remove one or multiple ids from the sniper (Seperate with commas)**\n"
                            f"**{self.prefix}kill** - **Kills the sniper**\n"
                            f"**{self.prefix}logs** - **Dumps the current log file**\n"
                            f"**{self.prefix}catfact** - **Provides you with a random cat fact to keep you busy whilst sniping.**",
                colour=discord.Colour.blue()
            ))

    async def start_bot(self):
        Visual.betterPrint("[COLOR_GREEN]Successfully started the discord bot", print_log=True)
        await self.start(conf.get("bot token", ""))
