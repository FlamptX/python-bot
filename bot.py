import os
from dotenv import load_dotenv
from pymongo import MongoClient
import asyncio
import datetime
import difflib
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle

users = []
code_message = None

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MY_TOKEN = os.getenv("MY_TOKEN")
TOKEN = os.getenv("TOKEN")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']

class Python(commands.Bot):
    def __init__(self):
        self.guild_db = db['guilds']
        self.user_db = db['users']

        self.prefix_cache = {}

        super().__init__(
            command_prefix=commands.when_mentioned_or(self.get_prefix),
            case_insensitive=True,
            intents=discord.Intents.default(),
            help_command=None
        )

    async def get_prefix(self, message):
        default_prefix = ["py ", "PY ", "Py ", "pY "]

        if not message.guild:
            return default_prefix

        guild_id = message.guild.id

        if guild_id in self.prefix_cache:
            return self.prefix_cache[guild_id]

        guild = self.guild_db.find_one({"_id": guild_id})

        data = {"_id": guild_id, "prefix": default_prefix}

        if guild["prefix"] is None:
            self.guild_db.insert_one(data)
            return default_prefix

        return guild['prefix']

    async def status_task(self):
        while True:
            await asyncio.sleep(3)
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                 name='py help in ' + str(
                                                                     len(self.guilds)) + ' servers'))
            await asyncio.sleep(30)
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                                 name='Python 3.8.1'))
            await asyncio.sleep(22)

bot = Python()

@bot.event
async def on_ready():
    bot.loop.create_task(bot.status_task())
    DiscordComponents(bot)

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

    print('The bot is online')

@bot.command()
async def ping(ctx):
    start = datetime.datetime.now()
    test_guild = bot.guild_db.find_one({"_id": 799328665442713600})
    end = datetime.datetime.now()
    seconds = (end - start).total_seconds()
    milliseconds = round(seconds * 1000)

    await ctx.send(f"Pong!\n**Bot latency:** {round(bot.latency * 1000)}ms\n**Database latency:** {milliseconds}ms")


@bot.command()
async def about(ctx):
    embed = discord.Embed(colour=discord.Colour.blue(), description=
    f"🐍   Python-Version • 3.8.6\n :page_facing_up:   Discord.py-Version • {discord.__version__}\n ** **\n 📡 Ping • {round(bot.latency * 1000)}ms\n 👾 Hostwebsite • SomethingHost \n :electric_plug: Database • MongoDB \n ** ** \n :chart_with_upwards_trend:  Servers • {len(bot.guilds)} \n :keyboard:  Commands • {len(bot.commands)}\n\nWebsite: https://python-bot.web.app")
    await ctx.send(embed=embed)


@bot.command()
async def info(ctx):
    embed_var = discord.Embed(title="Python Info",
                              description="> [**Official Python Site**](https://python.org) \n> [**About**](https://www.python.org/about/) \n> [**Downloads**](https://python.org/downloads) \n> [**Docs**](https://docs.python.org/) \n \n Latest version: [**DOWNLOAD 3.9.4**](https://www.python.org/downloads/release/python-394/)",
                              color=15844367)
    await ctx.send(embed=embed_var)


@bot.command()
async def invite(ctx):
    embed_var = discord.Embed(title="Invite",
                              description="Add me to other servers with this link: [**INVITE**](https://discord.com/api/oauth2/authorize?client_id=800832309989081118&permissions=388160&redirect_uri=https%3A%2F%2Fpython-bot.web.app&scope=bot) \n\nWebsite: https://python-bot.web.app\n\n Join the support server: https://discord.gg/wEWsdEKeEw",
                              color=3447003)
    await ctx.send(
        embed=embed_var,
        components=[
            [
                Button(style=ButtonStyle.URL, label="Invite",
                       url="https://discord.com/api/oauth2/authorize?client_id=800832309989081118&permissions=388160&redirect_uri=https%3A%2F%2Fpython-bot.web.app&scope=bot"),
                Button(style=ButtonStyle.URL, label="Support Server", url="https://discord.gg/wEWsdEKeEw"),
            ]
        ]
    )


@bot.command()
async def vote(ctx):
    embed_var = discord.Embed(title="Upvote",
                              description="You can support me by **upvoting on top.gg** \n [**VOTE HERE**](https://top.gg/bot/800832309989081118/vote)",
                              color=discord.Color.blue())
    await ctx.send(
        embed=embed_var,
        components=[
            [
                Button(style=ButtonStyle.URL, label="Upvote", url="https://top.gg/bot/800832309989081118/vote"),
            ]
        ]
    )


@bot.event
async def on_guild_join(guild):
    bot.guild_db.insert_one({"_id": guild.id, "prefix": ["py ", "PY ", "Py ", "pY "], "economy_disabled": False})


@bot.event
async def on_guild_remove(guild):
    bot.guild_db.delete_one({"_id": guild.id})


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        lst = []
        for i in bot.commands:
            lst.append(i.name)
        match = difflib.get_close_matches(ctx.message.content.split(' ')[1], lst, n=1)

        if len(match) == 0:
            return
        else:
            await ctx.send(f"Did you make a typo? Did you mean `{match[0]}`?")
        return
    elif isinstance(error, commands.MissingPermissions):
        try:
            await ctx.send("You cannot use this command. Missing `manage messages` permission")
        except Exception:
            print("Bot is missing permission")
        return
    elif isinstance(error.__cause__, discord.Forbidden):
        try:
            await ctx.send("I am missing permissions.")
        except Exception:
            print("Bot is missing permissions.")
        return
    elif isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.MemberNotFound):
        return
    if ctx.channel.id == 831462745316392990 or ctx.channel.id == 799698764935331852:
        embed = discord.Embed(title=":x: Error", colour=discord.Colour.red())
        embed.description = f'```\n{error}\n```'
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)
        return
    else:
        flampt = bot.get_user(621309926631014410) or await bot.fetch_user(621309926631014410)
        embed = discord.Embed(title=":x: Error", colour=discord.Colour.red())
        embed.description = f'```\n{error}\n```'
        embed.timestamp = datetime.datetime.utcnow()
        await flampt.send(embed=embed)
    raise error

bot.run(TOKEN)

# async def update_data():
#     while True:
#         requests.post("https://discord.com/api/v9/channels/799698764935331852/messages", headers=headers, data=data)
#
#         def check(msg):
#             return msg.author.id == 674885857458651161
#
#         message = await bot.wait_for('message', check=check, timeout=5)
#         file = await message.attachments[0].read()
#         lines = file.decode().splitlines()
#
#         i = 0
#         for line in lines:
#             user_id = line.split(",")[1]
#             try:
#                 member_exists = user_db.find_one({"_id": int(user_id)})
#                 if member_exists is not None:
#                     user = bot.get_user(int(user_id)) or await bot.fetch_user(int(user_id))
#                     users.append(user)
#                     await asyncio.sleep(2)
#                     i += 1
#                 else:
#                     continue
#             except ValueError:
#                 continue
#             if i == 10:
#                 break
#             await asyncio.sleep(1)
#         await asyncio.sleep(900)