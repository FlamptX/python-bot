from discord.ext import commands
from discord_components import Button, ButtonStyle
import inspect
import asyncio
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['guilds']

emojis = ["✅", "❌"]

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["changepref", "changeprefixes"])
    @commands.has_permissions(manage_messages=True)
    async def changeprefix(self, ctx, prefix):

        msg = await ctx.send(
            f"Do you want there to be space after the prefix?\n`{prefix}` > `{prefix} `",
            components=[
                [
                    Button(style=ButtonStyle.green, label="Yes"),
                    Button(style=ButtonStyle.red, label="No"),
                ]
            ]
        )

        while True:
            try:
                res = await self.bot.wait_for("button_click", timeout=15)
                if res.channel == ctx.channel and res.user.id == ctx.author.id:
                    if res.component.label == "Yes":
                        prefix += " "
                        collection.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}})
                        answer = f"Prefix was changed to `{prefix}`"
                    elif res.component.label == "No":
                        guild_prefix = collection.find_one({"_id": ctx.guild.id})["prefix"]
                        if type(guild_prefix) is list:
                            guild_prefix = guild_prefix[0]
                        answer = f"Leaving it as `{guild_prefix}`."
                    await res.respond(
                        type=7,
                        content=answer
                    )
                    break
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send(f"{ctx.author.mention} Prompt canceled due to no response.")
                break

    @commands.command(aliases=["defaultpref", "defaultprefixes"])
    @commands.has_permissions(manage_messages=True)
    async def defaultprefix(self, ctx):
        msg = await ctx.send(
            "Are you sure want to use the default prefix?",
            components=[
                [
                    Button(style=ButtonStyle.green, label="Yes"),
                    Button(style=ButtonStyle.red, label="No"),
                ]
            ]
        )

        while True:
            try:
                res = await self.bot.wait_for("button_click", timeout=15)
                if res.channel == ctx.channel and res.user.id == ctx.author.id:
                    if res.component.label == "Yes":
                        collection.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": ["py ", "PY ", "Py ", "pY "]}})
                        answer = "Prefix changed to `py`"
                    elif res.component.label == "No":
                        guild_prefix = collection.find_one({"_id": ctx.guild.id})["prefix"]
                        if type(guild_prefix) is list:
                            guild_prefix = guild_prefix[0]
                        answer = f"Leaving it as `{guild_prefix}`."
                    await res.respond(
                        type=7,
                        content=answer
                    )
                    break
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send(f"{ctx.author.mention} Prompt canceled due to no response.")
                break

    @commands.command(hidden=True)
    async def getcommand(self, ctx, arg):
        if ctx.author.id != 621309926631014410:
            return
        if arg == "help" or arg == "error":
            await ctx.send("Command is too long to be sent.")
            return
        elif arg == "getcommand":
            await ctx.send("No.")
            return
        cmds = self.bot.commands
        cmds_names = []
        for cmd in cmds:
            cmds_names.append(cmd.name)
        if any(s in arg for s in cmds_names):
            cmd = self.bot.get_command(arg)
            code = inspect.getsource(cmd.callback)
            await ctx.send(f"```{code}```")
        else:
            await ctx.send(":x:  That command either doesn't exist or you typed it incorrectly.")

    @getcommand.error
    async def getcommand_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(":x: Missing the command to get.")
            return

    @changeprefix.error
    async def changeprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(":x: The new prefix is missing. Correct command usage: `changeprefix <new prefix here>`")
            return
        raise error

def setup(bot):
    bot.add_cog(SettingsCog(bot))
