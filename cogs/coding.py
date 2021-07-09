from discord.ext import commands
import discord
import asyncio
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os
import random
bot_member = None

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['guilds']

class coding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["cc"])
    @commands.has_permissions(manage_messages=True)
    async def codechannel(self, ctx, *, arg=None):
        global bot_member
        if bot_member is None:
            bot_member = await ctx.guild.fetch_member(self.bot.user.id)
        if not bot_member.guild_permissions.manage_messages:
            await ctx.channel.send("I am missing the `manage_messages` permission.")
            return

        guild = collection.find_one({"_id": ctx.guild.id})

        try:
            code_channel = guild['code_channel']
        except KeyError:
            if arg is None:
                await ctx.send("Start a coding channel with `cc init`")
                return
        if arg is None or arg == "status":
            try:
                active = guild['code_channel_active']
                if active:
                    status = "Active :green_circle:"
                else:
                    status = "Inactive :red_circle:"
            except KeyError:
                status = "Inactive :red_circle:"

            embed = discord.Embed(title="Code Channel", description=f"Status: {status}\nChannel: <#833801030553829456>\n\n`help codechannel` for more information",
                                  colour=discord.Colour.gold(), timestamp=datetime.datetime.now())
            msg = await ctx.send(embed=embed)

            emoji = self.bot.get_emoji(833349328277471282)
            await msg.add_reaction(emoji)

            def check(react, react_user):
                return react_user == ctx.author and react.emoji.id == 833349328277471282

            try:
                await self.bot.wait_for("reaction_add", check=check, timeout=20)
                await msg.delete()
                await ctx.message.delete()

            except asyncio.TimeoutError:
                return
        elif "init" in arg or "initialize" in arg:
            try:
                msg_id = guild["code_channel_msg_id"]

                await ctx.channel.purge(limit=None)
                embed = discord.Embed(title="Coding Channel",
                                      description='```python\nprint("Hello World!")\n```\nSend anything to add it to the code.',
                                      colour=discord.Colour.from_rgb(255, 255, 0))
                try:
                    message = await ctx.channel.fetch_message(msg_id)
                    await message.edit(embed=embed)
                    message_id = message.id
                except discord.NotFound:
                    message_sent = await ctx.send(embed=embed)
                    message_id = message_sent.id

                collection.update_one({"_id": ctx.guild.id}, {
                    "$set": {"code_channel_active": True,
                             "code_channel_msg_id": message_id, "code_channel": ctx.channel.id}})

                embed = discord.Embed(title="Code Channel",
                                      description=f"The channel has been initialized for coding.\n",
                                      colour=discord.Colour.gold(), timestamp=datetime.datetime.now())
                msg = await ctx.send(embed=embed)

                await asyncio.sleep(2)
                await msg.delete()

            except KeyError:
                await ctx.send(f"This will delete all channel messages in <#{ctx.channel.id}>\nDo you want to proceed? `yes` or `no`")

                def check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for("message", check=check, timeout=15)
                    if msg.content.lower() == "yes":
                        await ctx.channel.purge(limit=None)
                        embed = discord.Embed(title="Coding Channel",
                                              description='```python\nprint("Hello World!")\n```\nSend anything to add it to the code.',
                                              colour=discord.Colour.from_rgb(255, 255, 0))

                        message = await ctx.send(embed=embed)

                        collection.update_one({"_id": ctx.guild.id}, {
                            "$set": {"code_channel_active": True,
                                     "code_channel_msg_id": message.id, "code_channel": ctx.channel.id}})

                        embed = discord.Embed(title="Code Channel",
                                              description=f"The channel has been initialized for coding.\n",
                                              colour=discord.Colour.gold(), timestamp=datetime.datetime.now())
                        msg = await ctx.send(embed=embed)

                        await asyncio.sleep(2)
                        await msg.delete()
                    elif msg.content.lower() == "no":
                        await ctx.send("Aborted.")
                        return
                except asyncio.TimeoutError:
                    await ctx.send("Coding channel initialization aborted due to no response.")
                    return

        elif "start" in arg:
            try:
                active = guild['code_channel_active']
                if active:
                    await ctx.send("The channel is already active.")
                    return
            except KeyError:
                pass

            collection.update_one({"_id": ctx.guild.id}, {"$set": {"code_channel_active": True}})

            msg = await ctx.send(":green_circle: Code channel has been started.")

            await asyncio.sleep(2)
            await msg.delete()
            await ctx.message.delete()
        elif "stop" in arg:
            try:
                active = guild['code_channel_active']
                if not active:
                    await ctx.send("The channel is already inactive.")
                    return
            except KeyError:
                pass

            collection.update_one({"_id": ctx.guild.id}, {"$set": {"code_channel_active": False}})

            msg = await ctx.send(":red_circle: Code channel has been stopped.")

            await asyncio.sleep(2)
            await msg.delete()
            await ctx.message.delete()
        elif "delete" in arg or "del" in arg:
            split_arg = arg.split()
            if len(split_arg) == 1:
                await ctx.send("You must specify the amount of lines to delete. Example: `cc delete 2`")
                return

            lines_num = split_arg[1]
            try:
                lines_num = int(lines_num)

                try:
                    msg = await ctx.channel.fetch_message(guild['code_channel_msg_id'])
                    content = msg.embeds[0].description.replace("Send anything to add it to the code.", "")

                    while "`" in content:
                        content = content.replace("`", "")

                    while content.startswith("""
"""):
                        content = content[1:]

                    if content.startswith("python"):
                        content = content[6:]

                    if 'print("Hello World!")' in content:
                        content = ""
                except discord.NotFound:
                    await ctx.send(
                        "It seems that the code message was deleted. Use `cc init` to send it again.")
                    return

                split_code = content.splitlines()
                while '' in split_code:
                    split_code.remove('')

                if (len(split_code) - lines_num) < 1:
                    msg = await ctx.send("There must be at least one line left when deleting.")
                    await asyncio.sleep(5)
                    await msg.delete()
                    await ctx.message.delete()
                    return

                split_code = split_code[:len(split_code) - lines_num]

                code = """
""".join(split_code)

                try:
                    msg = await ctx.channel.fetch_message(guild['code_channel_msg_id'])
                except discord.NotFound:
                    await ctx.channel.send("It seems that the code message was deleted. Use `cc init` to send it again.")
                    return

                embed = discord.Embed(title="Coding Channel",
                                      description=f"```python\n{code}```\nSend anything to add it to the code.",
                                      colour=discord.Colour.from_rgb(255, 255, 0))

                await msg.edit(embed=embed)

                if lines_num > 1:
                    l = "lines were"
                else:
                    l = "line was"
                bot_msg = await ctx.send(f"{lines_num} {l} deleted.")

                await asyncio.sleep(2)
                await bot_msg.delete()
                await ctx.message.delete()
            except ValueError:
                await ctx.send("That is not a number. Correct usage: `delete 2`")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        elif message.author.bot:
            await self.bot.process_commands(message)
            return

        guild = collection.find_one({"_id": message.guild.id})

        if message.content == "<@!800832309989081118>" or message.content == "<@800832309989081118>":
            prefix = await self.bot.get_prefix(message)

            if isinstance(prefix, list):
                prefix = prefix[0]

            await message.channel.send(random.choice([f"That's me! The server prefix is `{prefix}`", f"Hello! The server prefix is `{prefix}`", f"What's up? The server prefix is `{prefix}`"]))

        if guild is not None:
            try:
                active = guild['code_channel_active']
            except KeyError:
                pass
        else:
            await self.bot.process_commands(message)
            return

        prefix_there = message.content.startswith("py") or message.content.startswith(
            "Py") or message.content.startswith(
            "pY") or message.content.startswith("PY") or message.content.startswith('?')
        try:
            if message.channel.id == guild["code_channel"] and active and not prefix_there:

                bot_member = message.guild.get_member(self.bot.user.id) or await message.guild.fetch_member(self.bot.user.id)
                bot_perms = message.channel.permissions_for(bot_member)
                if not bot_perms.manage_messages:
                    await message.channel.send("I am missing the `manage_messages` permission.")
                    await self.bot.process_commands(message)
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
                    await message.channel.send(
                        "It seems that the code message was deleted. Use `cc init` to send it again.")
                    await self.bot.process_commands(message)
                    return
        except Exception:
            pass

def setup(bot):
    bot.add_cog(coding(bot))
