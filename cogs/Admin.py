from discord.ext import commands
import requests
import re
import aiohttp
import discord
import os, sys
from time import time
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
users = db['users']
guilds = db['guilds']


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def resolve_variable(self, variable):
        if hasattr(variable, "__iter__"):
            var_length = len(list(variable))
            if (var_length > 100) and (not isinstance(variable, str)):
                return f"<a {type(variable).__name__} iterable with more than 100 values ({var_length})>"
            elif not var_length:
                return f"<an empty {type(variable).__name__} iterable>"

        if (not variable) and (not isinstance(variable, bool)):
            return f"<an empty {type(variable).__name__} object>"
        return (variable if (
                    len(f"{variable}") <= 1000) else f"<a long {type(variable).__name__} object with the length of {len(f'{variable}'):,}>")

    def prepare(self, string):
        arr = string.strip("```").replace("py\n", "").replace("python\n", "").split("\n")
        if not arr[::-1][0].replace(" ", "").startswith("return"):
            arr[len(arr) - 1] = "return " + arr[::-1][0]
        return "".join(f"\n\t{i}" for i in arr)

    @commands.command(aliases=["restart"], hidden=True)
    @commands.is_owner()
    async def _restart(self, ctx):
        await ctx.send("Restarting...")
        os.system("python restart.py " + str(ctx.channel.id))
        sys.exit()

    @commands.command(aliases=['exec'], hidden=True)
    @commands.is_owner()
    async def _exec(self, ctx, *, code: str):
        silent = ("-s" in code)

        code = self.prepare(code.replace("-s", ""))
        args = {
            "discord": discord,
            "commands": commands,
            "users": users,
            "sys": sys,
            "os": os,
            "requests": requests,
            "imp": __import__,
            "self": self,
            "ctx": ctx,

        }

        try:
            exec(f"async def func():{code}", args)
            a = time()

            response = await eval("func()", args)
            if silent or (response is None) or isinstance(response, discord.Message):
                del args, code
                return

            await ctx.send(
                f"```py\n{self.resolve_variable(response)}````{type(response).__name__} | {(time() - a) / 1000} ms`")
        except Exception as e:
            await ctx.send(f"Error occurred:```\n{type(e).__name__}: {str(e)}```")

        del args, code, silent

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module: str):
        """Reloads a module."""
        if module == "all":
            i = 0
            j = 0
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        self.bot.unload_extension(f'cogs.{filename[:-3]}')
                        self.bot.load_extension(f'cogs.{filename[:-3]}')
                        i += 1
                    except Exception as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send('{}: {}'.format(type(e).__name__, e))
                    j += 1
            print(f'**{i}/{j}** extensions have been reloaded.')
            await ctx.send(f'**{i}/{j}** extensions have been reloaded.')
            return

        try:
            self.bot.unload_extension(f"cogs.{module}")
            self.bot.load_extension(f"cogs.{module}")
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            print(f'Extension {f"cogs.{module}"} has been reloaded.')
            await ctx.send(f'Extension {f"cogs.{module}"} has been reloaded.')

    @_reload.error
    async def _reload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing the module argument.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def react(self, ctx, msg_id: int):
        message = await ctx.channel.fetch_message(msg_id)
        await message.add_reaction("❓")
        await ctx.send("Done")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fixguilds(self, ctx):
        msg = await ctx.send("<a:loading_pic:833966183841529916> Deleting cached guilds...")
        guild_ids = []
        for guild in self.bot.guilds:
            guild_ids.append(guild.id)
        i = 0
        for document in guilds.find({}):
            if document["_id"] not in guild_ids:
                guilds.delete_one({"_id": document["_id"]})
                i += 1
        await msg.edit(content=f"Deleted {i} guilds.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def data(self, ctx):
        start = datetime.now()
        test_guild = guilds.find_one({"_id": 799328665442713600})
        end = datetime.now()
        seconds = (end - start).total_seconds()
        milliseconds = round(seconds * 1000)
        if milliseconds < 0:
            milliseconds = 0

        embed = discord.Embed(title="Admin Data",
                              description=f"Bot latency: {round(self.bot.latency * 1000)}ms\nDatabase latency: {milliseconds}ms\n\nGuild collection count: {guilds.count()}\nUsers collection count: {users.count()}",
                              colour=int("0x36393f", 16), timestamp=datetime.now())
        await ctx.send(embed=embed)

    @commands.command(aliases=["eval-send", "sendeval", "send-eval"], hidden=True)
    @commands.is_owner()
    async def evalsend(self, ctx, user_id=None, *, message):
        if user_id is None:
            await ctx.send("Missing the user argument.")
            return
        elif message is None:
            await ctx.send("Missing the message argument.")
            return
        user = await self.bot.fetch_user(int(user_id))
        await user.send(message)
        await ctx.send(f"Message sent to **{user.name}#{user.discriminator}**")

    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def stealemoji(self, ctx, msg_id: int, name=None):
        if ctx.guild.id == 799328665442713600:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(799328665442713600) or await self.bot.fetch_guild(799328665442713600)
        message = await ctx.channel.fetch_message(msg_id)
        content = message.content
        if "<:" in content or "<a:" in content:
            pattern = "<(.*?)>"

            content_emoji = re.search(pattern, content).group(1)
            if content_emoji.startswith("a:"):
                content_emoji = content_emoji.replace("a:", "")
                emoji_id = content_emoji.split(":")[1]
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://cdn.discordapp.com/emojis/{emoji_id}.gif", allow_redirects=True) as resp:
                        r = await resp.read()
                if r == b'':
                    await ctx.send("Couldn't find the url for that emoji.")
                    return
                if name is None:
                    name = content_emoji.split(":")[0]
                emoji = await guild.create_custom_emoji(image=r, name=name)
                await ctx.send(f"Emoji <a:{emoji.name}:{emoji.id}> has been stolen and added!")
            else:
                emoji_id = content_emoji.split(":")[2]
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://cdn.discordapp.com/emojis/{emoji_id}.png", allow_redirects=True) as resp:
                        r = await resp.read()
                if r == b'':
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://cdn.discordapp.com/emojis/{emoji_id}.jpg", allow_redirects=True) as resp:
                            r = await resp.read()
                    if r == b'':
                        await ctx.send("Could't find the url for that emoji.")
                        return
                if name is None:
                    name = content_emoji.split(":")[1]
                emoji = await guild.create_custom_emoji(image=r, name=name)
                await ctx.send(f"Emoji <:{emoji.name}:{emoji.id}> has been stolen and added!")

    @stealemoji.error
    async def stealemoji_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            await ctx.send(":x: Wrong command usage. Correct usage: `stealemoji <message id>`")
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You can't use that command.")
            return
        elif isinstance(error.__cause__, discord.Forbidden):
            return
        raise error

    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def makeemoji(self, ctx, name, url=None):
        if url:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, allow_redirects=True) as resp:
                    file_request = await resp.read()
            try:
                emoji = await ctx.guild.create_custom_emoji(image=file_request, name=name)
                await ctx.send(f"Emoji <:{emoji.name}:{emoji.id}> was created!")
            except discord.InvalidArgument:
                await ctx.send("You must attach an **image** or a **gif** for the emoji, not a different type of the file.")
            return
        try:
            url = ctx.message.attachments[0].url
        except IndexError:
            await ctx.send("You must attach an image or a gif for the emoji.")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True) as resp:
                file_request = await resp.read()
        try:
            emoji = await ctx.guild.create_custom_emoji(image=file_request, name=name)
        except discord.InvalidArgument:
            await ctx.send("You must attach an **image** or a **gif** for the emoji, not a different type of the file.")
            return
        await ctx.send(f"Emoji <:{emoji.name}:{emoji.id}> was created!")

    @makeemoji.error
    async def makeemoji_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Specify a name for the emoji. Example: `makeemoji emoji1`")
            return
        raise error

    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def addemoji(self, ctx, emoji: discord.PartialEmoji, name=None):
        asset = emoji.url_as()
        if not name:
            name = emoji.name
        emoji = await ctx.guild.create_custom_emoji(image=await asset.read(), name=name)
        await ctx.send(f"Emoji <:{emoji.name}:{emoji.id}> was added!")

    @addemoji.error
    async def addemoji_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument given, it must be an emoji.")
            return
        raise error

    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx, *, module: str):
        if ctx.author.id != 621309926631014410:
            return
        """Reloads a module."""
        if module == "all":
            i = 0
            j = 0
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        self.bot.unload_extension(f'cogs.{filename[:-3]}')
                        self.bot.load_extension(f'cogs.{filename[:-3]}')
                        i += 1
                    except Exception as e:
                        print('{}: {}'.format(type(e).__name__, e))
                        await ctx.send('{}: {}'.format(type(e).__name__, e))
                    j += 1
            print(f'**{i}/{j}** extensions have been reloaded.')
            await ctx.send(f'**{i}/{j}** extensions have been reloaded.')
            return

        try:
            self.bot.unload_extension(f"cogs.{module}")
            self.bot.load_extension(f"cogs.{module}")
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        els
            print(f'Extension {f"cogs.{module}"} has been reloaded.')
            await ctx.send(f'Extension {f"cogs.{module}"} has been reloaded.')

    @_reload.error
    async def _reload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing the module argument.")

def setup(bot):
    bot.add_cog(Admin(bot))
