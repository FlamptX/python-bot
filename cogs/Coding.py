from discord.ext import commands
import discord
import asyncio
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os
bot_member = None

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['guilds']

class Coding(commands.Cog):
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

def setup(bot):
    bot.add_cog(Coding(bot))
