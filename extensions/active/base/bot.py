import discord
from discord.ext import commands
import logging
import os
import time
import json
import aiohttp

from themes.required.sniper import UGCSniper
from themes.required.visual import Visual
from __main__ import conf


class Bot(commands.Bot):
    def __init__(self, sniper: UGCSniper):
        self.sniper = sniper
        self.prefix = conf.get("prefix", ">")

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

            _added = [f"> **{_id}** - **{self.sniper.limitednames.get(str(_id), 'N/A')}**" for _id in self.sniper.limiteds]
            added = []
            for idx, item in enumerate(_added):
                if len(item) + len(str(added)) >= 1024:
                    added.append(f"> **{len(_added)-idx} left. . .**")
                    break

                added.append(item)

            embed.add_field(name="Added ids", value="\n".join(added), inline=True)
            embed.set_footer(text=f"Requested by: {ctx.author.display_name}", icon_url=ctx.author.display_avatar)

            await ctx.send(embed=embed)

        @self.command("add")
        async def add_limiteds(ctx: commands.Context, *, ids:str):
            logging.info(f"Add command executed with the following limiteds: {ids}")
            ids = ids.replace(" ", "").split(",")

            self.sniper.limiteds += ids
            for _id in ids: self.sniper.limitednames[str(_id)] = "N/A"
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
            _added = [f"> **{_id}** - **{self.sniper.limitednames.get(str(_id), 'N/A')}**" for _id in self.sniper.limiteds]
            added = []
            for idx, item in enumerate(_added):
                if len(item) + len(str(added)) >= 1024:
                    added.append(f"> **{len(_added)-idx} left. . .**")
                    break

                added.append(item)
            ids = "\n".join(added)

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
            _added = [f"> **{_id}** - **{self.sniper.limitednames.get(str(_id), 'N/A')}**" for _id in self.sniper.limiteds]
            added = []
            for idx, item in enumerate(_added):
                if len(item) + len(str(added)) >= 1024:
                    added.append(f"> **{len(_added)-idx} left. . .**")
                    break

                added.append(item)
            added = "\n".join(added)

            await ctx.send(embed=discord.Embed(
                title="Showing mode info",
                description=f"Mode: **{self.sniper.mode}**\n"
                            f"Starting in: {timestamp}\n\n"
                            f"Cooldown: **{self.sniper.cooldown}** seconds\n"
                            f"Added limiteds: \n"
                            f"{added}",
                colour=discord.Colour.green()
            ))

        @self.command("cooldown")
        async def cooldown(ctx: commands.Context, cooldown):
            logging.info(f"Cooldown command executed with a cooldown of {cooldown}")
            try: self.sniper.cooldown = float(cooldown)
            except ValueError:
                await ctx.send(embed=discord.Embed(
                    title="ERROR - No valid cooldown parsed",
                    description="**Failed setting cooldown because no valid cooldown was given.**",
                    colour=discord.Colour.red()
                ))
                return
            await ctx.send(embed=discord.Embed(
                title="Successfully set the cooldown",
                description=f"**Successfully set the cooldown to {cooldown} seconds.**",
                colour=discord.Colour.green()
            ))

        @self.command("clear")
        async def _clear(ctx: commands.Context):
            self.sniper.limiteds = []
            self.sniper.limitednames = {}

            await ctx.send(embed=discord.Embed(
                title="Successfully cleared every limited.",
                description="Successfully cleared every limited.\n"
                            "To add a limited remember use the add command.\n\n"
                            "**THIS ACTION CAN BE UNDONE BY RESTARTING THE SNIPER**",
                color=discord.Colour.green()
            ))

        @self.command("pause")
        async def pause(ctx: commands.Context, minutes: int = -1):
            if minutes != -1: self.sniper.minutes = minutes
            else:
                await ctx.send(embed=discord.Embed(
                    title="No pause time given.",
                    description="No amount of time to pause was given.\n"
                                f"Please use the following command to pause: {self.prefix}pause 5"
                ))
                return
            await ctx.send(embed=discord.Embed(
                title="Successfully paused the sniper.",
                description="Successfully paused the sniper.\n"
                            "Please keep in mind that only checking has been paused anything else isnt paused.\n\n"
                            "**THIS ACTION CAN BE UNDONE BY THE >unpause COMMAND**",
                color=discord.Colour.green()
            ))

        @self.command("unpause")
        async def unpause(ctx: commands.Context):
            self.sniper.minutes = 0
            await ctx.send(embed=discord.Embed(
                title="Successfully unpaused the sniper.",
                description="Successfully unpaused the sniper.\n"
                            "The sniper is now checking the limiteds again.",
                color=discord.Colour.green()
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
                            f"**{self.prefix}cooldown** - **Sets the cooldown for the sniper.**\n"
                            f"**{self.prefix}clear** - **Clears every limited. (Cannot be undone automatically)**\n"
                            f"**{self.prefix}pause** - **Pauses the sniper.**\n"
                            f"**{self.prefix}unpause** - **Unpauses the sniper**\n"
                            f"**{self.prefix}catfact** - **Provides you with a random cat fact to keep you busy whilst sniping.**",
                colour=discord.Colour.blue()
            ))

    async def start_bot(self):
        Visual.betterPrint("[COLOR_GREEN]Successfully started the discord bot", print_log=True)
        await self.start(conf.get("bot token", ""))
