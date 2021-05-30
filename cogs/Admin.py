from discord.ext import commands
import requests
import re
import aiohttp
import discord
import os
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

    @commands.command(hidden=True)
    async def react(self, ctx, msg_id: int):
        message = await ctx.channel.fetch_message(msg_id)
        await message.add_reaction("❓")
        await ctx.send("Done")

    @commands.command(hidden=True)
    async def fixguilds(self, ctx):
        if ctx.author.id != 621309926631014410:
            return
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
    async def data(self, ctx):
        if ctx.author.id != 621309926631014410:
            return
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
    async def evalsend(self, ctx, user_id=None, *, message):
        if user_id is None:
            await ctx.send("Missing the user argument.")
            return
        elif message is None:
            await ctx.send("Missing the message argument.")
            return
        if ctx.author.id == 621309926631014410:
            user = await self.bot.fetch_user(int(user_id))
            await user.send(message)
            await ctx.send(f"Message sent to **{user.name}#{user.discriminator}**")

    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def stealemoji(self, ctx, msg_id: int, name=None):
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
                emoji = await ctx.guild.create_custom_emoji(image=r, name=name)
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
                emoji = await ctx.guild.create_custom_emoji(image=r, name=name)
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
        else:
            print(f'Extension {f"cogs.{module}"} has been reloaded.')
            await ctx.send(f'Extension {f"cogs.{module}"} has been reloaded.')

    @_reload.error
    async def _reload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing the module argument.")

def setup(bot):
    bot.add_cog(Admin(bot))

#     @commands.command()
#     async def send(self, ctx):
#         channel = await self.bot.fetch_channel(841398524208873492)
#         embed = discord.Embed(title="Read before opening a question",
#                               description="> Before opening a question search the answer online or in <#841398408988065852>\n> If it's something easy to fix or answer rather ask in other channels such as <#799338437308055572>\n> **Do not** spam open questions because you can lose permission to open them permanently",
#                               colour=discord.Colour.red())
#         await channel.send(embed=embed)
#
#     @commands.command()
#     async def send2(self, ctx):
#         channel = await self.bot.fetch_channel(841398524208873492)
#         embed = discord.Embed(title="Information",
#                               description="You can create questions for help with your code or to ask something.\nBefore that you need to make a profile with `createprofile` in <#799368863720144896>\n\nAnswering, commenting, marking answers as the solution and getting answers marked as the solution will give you points.\nAt certain amounts of points you will get a new rank and a role.\nRanks:\n```python\n1 | Starter | 500 Points\n2 | Intermediate | 1500 Points\n3 | Active Helper | 3000 Points\n4 | Dev Nerd | 10000 Points\n5 | Stack Pro | 50000 Points\n```",
#                               colour=discord.Colour.orange())
#         await channel.send(embed=embed)
