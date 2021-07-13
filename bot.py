import os
from dotenv import load_dotenv
from pymongo import MongoClient
import asyncio
import datetime
import difflib
import discord
from discord.ext import commands
from discord_components import DiscordComponents
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("id", nargs='?', default=None)
args = parser.parse_args()

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
            command_prefix=self.get_prefix,
            case_insensitive=True,
            intents=discord.Intents.default(),
            help_command=None
        )

    async def get_prefix(self, message):
        default_prefix = ["py ", "PY ", "Py ", "pY "]

        if not message.guild:
            return commands.when_mentioned_or(*default_prefix)(self, message)

        guild_id = message.guild.id

        if guild_id in self.prefix_cache:
            if isinstance(self.prefix_cache[guild_id], str):
                self.prefix_cache[guild_id] = [self.prefix_cache[guild_id]]

            return commands.when_mentioned_or(*self.prefix_cache[guild_id])(self, message)

        guild = self.guild_db.find_one({"_id": guild_id})

        data = {"_id": guild_id, "prefix": default_prefix}

        if guild["prefix"] is None:
            self.guild_db.insert_one(data)
            self.prefix_cache[guild_id] = default_prefix
            return commands.when_mentioned_or(*default_prefix)(self, message)

        if isinstance(guild['prefix'], str):
            guild['prefix'] = [guild['prefix']]

        self.prefix_cache[guild_id] = guild["prefix"]
        return commands.when_mentioned_or(*guild['prefix'])(self, message)

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

    if args.id is not None:
        channel = bot.get_channel(int(args.id)) or await bot.fetch_channel(int(args.id))
        await channel.send("Bot has been restarted!")

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