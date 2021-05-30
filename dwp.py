import os
from dotenv import load_dotenv
from pymongo import MongoClient
import random
import asyncio
import datetime
import difflib
import requests
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
users = []
code_message = None

load_dotenv()
TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
MY_TOKEN = os.getenv("MY_TOKEN")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['guilds']
user_db = db['users']

def get_prefix(bot, message):
    if not message.guild:
        return
    id = message.guild.id
    pref = collection.find_one({"_id": id})
    post = {"_id": id, "prefix": ["py ", "PY ", "Py ", "pY "]}
    if pref is None:
        collection.insert_one(post)
        return ["py ", "PY ", "Py ", "pY "]
    else:
        if pref['prefix'] is not None:
            return pref['prefix']
        return ["py ", "PY ", "Py ", "pY "]

bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True, intents=discord.Intents.default())

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

async def status_task():
    while True:
        await asyncio.sleep(3)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                            name='py help in ' + str(len(bot.guilds)) + ' servers'))
        await asyncio.sleep(30)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                            name='Python 3.8.6'))
        await asyncio.sleep(22)

headers = {
    "authorization": os.getenv("MY_TOKEN")
}

data = {
    "content": "!d bump"
}

async def bump():
    while True:
        requests.post("https://discord.com/api/v9/channels/799698764935331852/messages", headers=headers, data=data)
        await asyncio.sleep(random.randint(7205, 7215))

async def update_data():
    while True:
        requests.post("https://discord.com/api/v9/channels/799698764935331852/messages", headers=headers, data=data)

        def check(msg):
            return msg.author.id == 674885857458651161
        message = await bot.wait_for('message', check=check, timeout=5)
        file = await message.attachments[0].read()
        lines = file.decode().splitlines()

        i = 0
        for line in lines:
            user_id = line.split(",")[1]
            try:
                member_exists = user_db.find_one({"_id": int(user_id)})
                if member_exists is not None:
                    user = bot.get_user(int(user_id)) or await bot.fetch_user(int(user_id))
                    users.append(user)
                    await asyncio.sleep(2)
                    i += 1
                else:
                    continue
            except ValueError:
                continue
            if i == 10:
                break
            await asyncio.sleep(1)
        await asyncio.sleep(900)

@bot.event
async def on_ready():
    bot.loop.create_task(status_task())
    # bot.loop.create_task(update_data())
    bot.loop.create_task(bump())
    DiscordComponents(bot)
    print('The bot is online')

@bot.event
async def on_message(message):
    if not message.guild:
        return
    elif message.author.bot:
        await bot.process_commands(message)
        return

    guild = collection.find_one({"_id": message.guild.id})

    try:
        if guild is not None:
            active = guild['code_channel_active']
        else:
            await bot.process_commands(message)
            return
    except KeyError:
        await bot.process_commands(message)
        return

    prefix_there = message.content.startswith("py") or message.content.startswith("Py") or message.content.startswith("pY") or message.content.startswith("PY") or message.content.startswith('?')
    try:
        if message.channel.id == guild["code_channel"] and active and not prefix_there:

            bot_member = message.guild.get_member(bot.user.id) or await message.guild.fetch_member(bot.user.id)
            bot_perms = message.channel.permissions_for(bot_member)
            if not bot_perms.manage_messages:
                await message.channel.send("I am missing the `manage_messages` permission.")
                await bot.process_commands(message)
                return

            code = message.content

            bot_msg = await message.channel.send("<a:loading_pic:833966183841529916> Adding your code...")

            while "`" in code:
                code = code.replace("`", "")
            if code.startswith("""
"""):
                code = code[1:]

            if len(code) > 100 and message.author.id != 621309926631014410:
                await bot_msg.delete()
                msg = await message.channel.send("Maximum of 100 characters per message is allowed.")
                await asyncio.sleep(5)
                await msg.delete()
                await message.delete()
                await bot.process_commands(message)
                return

            try:
                global code_message
                if code_message is None:
                    msg = await message.channel.fetch_message(guild['code_channel_msg_id'])
                    code_message = msg
                else:
                    msg = code_message
                content = msg.embeds[0].description.replace("Send anything to add it to the code.", "")

                while "`" in content:
                    content = content.replace("`", "")

                    if content.startswith("""
"""):
                        content = content[1:]

                if content.startswith("python"):
                    content = content[6:]

                if 'print("Hello World!")' in content:
                    content = ""

                embed = discord.Embed(title="Coding Channel",
                                      description=f"```python\n{content}{code}```\nSend anything to add it to the code.",
                                      colour=discord.Colour.from_rgb(255, 255, 0))

                await msg.edit(embed=embed)

                await bot_msg.delete()
                await message.delete()
            except discord.NotFound:
                print(guild['code_channel_msg_id'])
                await bot_msg.delete()
                await message.channel.send("It seems that the code message was deleted. Use `cc init` to send it again.")
                await bot.process_commands(message)
                return
    except KeyError:
        pass

    msg = message.content.lower()
    mentioned = bot.user.mentioned_in(message)
    if mentioned and message.reference is None and len(msg.split()) < 2:
        if type(get_prefix(None, message)) is not list:
            prefix = get_prefix(None, message)
        else:
            prefix = "py "
        try:
            await message.channel.send(f"The prefix is `{prefix}` For more info send `{prefix}help`")
        except discord.Forbidden:
            print("Missing permission to send message.")

    if message.channel.id in [799338437308055572, 799339140289527848] and any(phrase in message.content for phrase in ["ctx", "bot.command", "on_message", "discord."]):
        embed = discord.Embed(title="Please keep it organized", description="It seems that you are talking about discord.py in the wrong channel so please move to <#799338868818182145>", colour=discord.Colour.red())
        embed.set_footer(text="Ignoring this message will end up with a warn")

        await message.channel.send(embed=embed)

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    start = datetime.datetime.now()
    test_guild = collection.find_one({"_id": 799328665442713600})
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
                Button(style=ButtonStyle.URL, label="Invite", url="https://discord.com/api/oauth2/authorize?client_id=800832309989081118&permissions=388160&redirect_uri=https%3A%2F%2Fpython-bot.web.app&scope=bot"),
                Button(style=ButtonStyle.URL, label="Support Server", url="https://discord.gg/wEWsdEKeEw"),
            ]
        ]
    )

@bot.command()
async def vote(ctx):
    embed_var = discord.Embed(title="Upvote",
                              description="You can support me by **upvoting on top.gg** \n [**VOTE HERE**](https://top.gg/bot/800832309989081118/vote)", color=discord.Color.blue())
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
    collection.insert_one({"_id": guild.id, "prefix": ["py ", "PY ", "Py ", "pY "], "economy_disabled": False})

@bot.event
async def on_guild_remove(guild):
    collection.delete_one({"_id": guild.id})

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
