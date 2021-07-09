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

class config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["changepref", "changeprefixes"], help="Change the server prefix. | `MANAGE_SERVER`", description="prefix (Required): The new prefix", usage="changeprefix <prefix>")
    @commands.has_permissions(manage_server=True)
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

    @commands.command(aliases=["defaultpref", "defaultprefixes"], help="Set the default prefix which is `py` | `MANAGE_SERVER`", description="This command takes no arguments.", usage="defaultprefix")
    @commands.has_permissions(manage_server=True)
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
                if res.message.id == msg.id and res.user.id == ctx.author.id:
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
    @commands.is_owner()
    async def getcommand(self, ctx, arg):
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

    @commands.command(aliases=["economy-toggle", "economytoggle", "toggle-economy"], help="Enable or disable economy in the server. | `MANAGE_SERVER`", description="option (Required): It can either be `enable` or  `disable`", usage="toggleeconomy <option>")
    @commands.has_permissions(manage_server=True)
    async def toggleeconomy(self, ctx, option: str = None):
        guild = guilds.find_one({"_id": ctx.guild.id})
        if option is None:
            await ctx.send(
                "Use this command to toggle the economy for this guild.\nUsage: `economy on` or `economy off`")
        elif option.lower() in ["enable", "on"]:
            if guild["economy_disabled"]:
                guilds.update_one({"_id": ctx.guild.id}, {"$set": {"economy_disabled": False}})
                await ctx.send("Economy has been enabled.")
            else:
                await ctx.send("Economy is already enabled for this guild.")
        elif option.lower() in ["disable", "off"]:
            if not guild["economy_disabled"]:
                guilds.update_one({"_id": ctx.guild.id}, {"$set": {"economy_disabled": True}})
                await ctx.send("Economy has been disabled.")
            else:
                await ctx.send("Economy is already disabled for this guild.")
        else:
            await ctx.send("That's not an option, use `on` or `off`")

    @toggleeconomy.error
    async def economy_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You are missing the `manage_messages` permission to use this command.")

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
    bot.add_cog(config(bot))
