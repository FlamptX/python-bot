import discord
from discord.ext import commands
import asyncio
import random
import datetime
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import difflib
from dwp import users as u

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['users']
guilds = db['guilds']

jobs1 = ["discord bot developer", "computer engineer at a small tech company",
         "hosting service provider"]
jobs2 = ["developer at top.gg", "web developer", "tech company owner", "game designer"]
jobs3 = ["data scientist", "cloud engineer", "full stack developer", "mobile games developer"]
jobs4 = ["software engineer at JetBrains", "software engineer at Google", "IT security specialist", "system engineer",
         "software engineer at Facebook"]

parts1 = ["cable", "hard disk", "ram", "fan", "psu"]
parts2 = ["cpu", "motherboard", "graphics card"]
parts3 = ["water cooler tank", "water cooler pipe", "ssd"]

cable_price = random.randint(50, 75)
fan_price = random.randint(75, 150)
harddisk_price = random.randint(75, 100)
ram_price = random.randint(175, 250)
cpu_price = random.randint(350, 700)
motherboard_price = random.randint(250, 500)
graphicscard_price = random.randint(400, 750)
tank_price = random.randint(100, 125)
pipe_price = random.randint(80, 110)
ssd_price = random.randint(150, 200)
psu_price = random.randint(200, 250)

def item_emoji(part):
    if part == "cable":
       return "<:powerplug:831458832013590569>"
    elif part == "fan":
        return "<:fan:831458831690760192>"
    elif part == "hard disk":
        return "<:harddisk:831458831786573834>"
    elif part == "ram":
        return "<:ram_1:831458832064446465>"
    elif part == "cpu":
        return "<:cpu:831458831388770335>"
    elif part == "motherboard":
        return "<:motherboard:831458831811870720>"
    elif part == "graphics card":
        return "<:graphicscard:831458831493890079>"
    elif part == "water cooler tank":
        return "<:tank:831458832131686411>"
    elif part == "water cooler pipe":
        return "<:pipe:831458831900999690>"
    elif part == "psu":
        return "<:power:831458832001138728>"
    else:
        return ""

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["economy-toggle", "economytoggle", "toggle-economy"])
    @commands.has_permissions(manage_messages=True)
    async def toggleeconomy(self, ctx, option: str = None):
        guild = guilds.find_one({"_id": ctx.guild.id})
        if option is None:
            await ctx.send("Use this command to toggle the economy for this guild.\nUsage: `economy on` or `economy off`")
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

    @commands.command()
    async def startcareer(self, ctx):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        try:
            collection.insert_one({"_id": ctx.author.id, "level": "1.0", "money": 100, "job": "freelancer", "inventory": ["low budget laptop", "slow wifi router"], "antivirus_work": 0})
        except Exception:
            await ctx.send(
                f"{ctx.author.mention} you already have a career. If you want to quit use `quit`")
            return
        await ctx.send(
            f"**{ctx.author.mention} You have started your career**\nYou are starting as a __freelancer__ with a __low budget laptop__. Start earning some money by working or starting a company and leveling up.\nFor more information use `help economy`")

    @commands.command()
    async def quit(self, ctx):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You haven't started your career. Use `startcareer`")
        else:
            if user["job"] == "Company Owner":
                await ctx.send("You're a company owner. Use `shutdowncompany` if you don't want it anymore.")
            elif user["job"] == "Not hired":
                await ctx.send("You don't have a job.")
            else:
                collection.update_one({"_id": ctx.author.id}, {"$set": {"job": "Not hired"}})
                await ctx.send(f"{ctx.author.mention} you have quit your job. If you want to get a new job use `findjob`")

    @commands.command()
    async def findjob(self, ctx):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        if user["job"] != "Not hired":
            await ctx.send("You already have a job. If you want a new one you first must quit with `quit`")
            return
        if float(user["level"]) < 3.0:
            await ctx.send("You can only be a freelancer at this level.")
            collection.update_one({"_id": ctx.author.id}, {"$set": {"job": "freelancer"}})
            return
        elif 3.0 <= float(user["level"]) < 7.0:
            job = random.choice(jobs1)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"job": job}})
        elif 7.0 <= float(user["level"]) < 15.0:
            job = random.choice(jobs2)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"job": job}})
        elif 15.0 <= float(user["level"]) < 25.0:
            job = random.choice(jobs3)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"job": job}})
        else:
            job = random.choice(jobs4)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"job": job}})
        await ctx.send(f"You now work as a {job}.")

    @commands.command(aliases=["bal", "balance"])
    async def career(self, ctx, member: discord.Member = None):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        if member is None:
            user = collection.find_one({"_id": ctx.author.id})
            if user is None:
                await ctx.send("You must have a career, use `startcareer`")
                return
            level = "□□□□□□□□□□"
            number_dec = user['level'][-2:]
            number_dec = float(number_dec)
            if number_dec == 0.1:
                level = "■□□□□□□□□□"
            elif number_dec == 0.2:
                level = "■■□□□□□□□□"
            elif number_dec == 0.3:
                level = "■■■□□□□□□□"
            elif number_dec == 0.4:
                level = "■■■■□□□□□□"
            elif number_dec == 0.5:
                level = "■■■■■□□□□□"
            elif number_dec == 0.6:
                level = "■■■■■■□□□□"
            elif number_dec == 0.7:
                level = "■■■■■■■□□□"
            elif number_dec == 0.8:
                level = "■■■■■■■■□□"
            elif number_dec == 0.9:
                level = "■■■■■■■■■□"
            job = user['job']
            if job == "freelancer":
                payout = "$150-$250"
            elif job in jobs1:
                payout = "$300-$450"
            elif job in jobs2:
                payout = "$500-$750"
            elif job in jobs3:
                payout = "$1000-$1500"
            elif job in jobs4:
                payout = "$2000-$3000"
            elif job == "Company Owner":
                payout = ""
            else:
                payout = "$0"
            job_fixed = job[0].upper() + job[1:]
            if payout != "":
                description = f"**Employment**\n**- {job_fixed}**\nPayout: {payout}\n\n**Balance**ㅤㅤㅤㅤㅤㅤ\n:dollar: **${user['money']}**\n\n**Level**\n:large_blue_diamond: **{str(user['level'])[:-2]}** [{level}](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
            else:
                description = f"**Employment**\n**- {job_fixed}**\n\n**Balance**ㅤㅤㅤㅤㅤㅤ\n:dollar: **${user['money']}**\n\n**Level**\n:large_blue_diamond: **{str(user['level'])[:-2]}** [{level}](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
            em = discord.Embed(title=f"{ctx.author.name}'s career",
                               description=description,
                               colour=discord.Colour.orange())
            em.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send(embed=em)
        else:
            user = collection.find_one({"_id": member.id})
            if user is None:
                await ctx.send("That user doesn't have a career.")
                return
            level = "□□□□□□□□□□"
            number_dec = user['level'][-2:]
            number_dec = float(number_dec)
            if number_dec == 0.1:
                level = "■□□□□□□□□□"
            elif number_dec == 0.2:
                level = "■■□□□□□□□□"
            elif number_dec == 0.3:
                level = "■■■□□□□□□□"
            elif number_dec == 0.4:
                level = "■■■■□□□□□□"
            elif number_dec == 0.5:
                level = "■■■■■□□□□□"
            elif number_dec == 0.6:
                level = "■■■■■■□□□□"
            elif number_dec == 0.7:
                level = "■■■■■■■□□□"
            elif number_dec == 0.8:
                level = "■■■■■■■■□□"
            elif number_dec == 0.9:
                level = "■■■■■■■■■□"
            job = user['job']
            if job == "freelancer":
                payout = "$150-$250"
            elif job in jobs1:
                payout = "$300-$450"
            elif job in jobs2:
                payout = "$500-$750"
            elif job in jobs3:
                payout = "$1000-$1500"
            elif job in jobs4:
                payout = "$2000-$3000"
            elif job == "Company Owner":
                payout = ""
            else:
                payout = "$0"
            job_fixed = job[0].upper() + job[1:]
            if payout != "":
                description = f"**Employment**\n**- {job_fixed}**\nPayout: {payout}\n\n**Balance**ㅤㅤㅤㅤㅤㅤ\n:dollar: **${user['money']}**\n\n**Level**\n:large_blue_diamond: **{str(user['level'])[:-2]}** [{level}](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
            else:
                description = f"**Employment**\n**- {job_fixed}**\n\n**Balance**ㅤㅤㅤㅤㅤㅤ\n:dollar: **${user['money']}**\n\n**Level**\n:large_blue_diamond: **{str(user['level'])[:-2]}** [{level}](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
            em = discord.Embed(title=f"{member.name}'s career",
                               description=description,
                               colour=discord.Colour.orange())
            em.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=em)

    @commands.command(aliases=["add-money"])
    async def addmoney(self, ctx, member: discord.Member, money):
        if ctx.author.id != 621309926631014410:
            return
        if member:
            user = collection.find_one({"_id": member.id})
            if user is None:
                await ctx.send("That user doesn't have a career.")
                return
        else:
            user = collection.find_one({"_id": ctx.author.id})
            if user is None:
                await ctx.send("You must have a career, use `startcareer`")
                return
        collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + int(money)}})
        await ctx.send(f"Added ${money} to {member.name}#{member.discriminator}")

    @commands.command()
    async def work(self, ctx):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        if user['job'] == "Company Owner":
            await ctx.send("You can't use this command, you're a company owner.")
            return
        elif user['job'] == "Not hired":
            await ctx.send("You don't have a job. Use `findjob` to get one")
            return
        try:
            last_work = user["last_work"]
            can_work = datetime.datetime.strptime(last_work, "%Y-%m-%d %H:%M:%S")
            if can_work >= datetime.datetime.now().replace(microsecond=0):
                duration = can_work - datetime.datetime.now()
                seconds = duration.total_seconds()
                minutes = round(seconds // 60)
                seconds = round(seconds % 60)
                if minutes == 0:
                    await ctx.send(
                        f"{ctx.author.mention} You must wait **{seconds} seconds** to work again.")
                elif seconds == 0:
                    await ctx.send(
                        f"{ctx.author.mention} You must wait **{minutes} minutes** to work again.")
                else:
                    await ctx.send(
                        f"{ctx.author.mention} You must wait **{minutes} minutes and {seconds} seconds** to work again.")
                return
        except KeyError:
            pass

        date = datetime.datetime.now().replace(microsecond=0)
        if ctx.channel.id == 831462745316392990:
            date += datetime.timedelta(seconds=5)
        elif "good wifi router" in user["inventory"]:
            date += datetime.timedelta(minutes=10)
        elif "very fast wifi router" in user["inventory"]:
            date += datetime.timedelta(minutes=8)
        else:
            date += datetime.timedelta(minutes=15)
        collection.update_one({"_id": ctx.author.id},
                              {"$set": {"last_work": str(date)}})

        if ctx.channel.id == 831462745316392990:
            payout = 0
        elif user['job'] == "freelancer":
            payout = random.randint(150, 250)
        elif user['job'] in jobs1:
            payout = random.randint(300, 450)
        elif user['job'] in jobs2:
            payout = random.randint(500, 750)
        elif user['job'] in jobs3:
            payout = random.randint(1000, 1500)
        elif user['job'] in jobs4:
            payout = random.randint(2000, 3000)
        else:
            payout = 0

        if "high quality laptop" in user["inventory"]:
            remove = "high quality laptop"
            break_laptop = random.randint(1, 100) <= 4 and user["money"] > 4500
        elif "average laptop" in user["inventory"]:
            remove = "average laptop"
            break_laptop = random.randint(1, 100) <= 11 and user["money"] > 2000
        elif "low budget laptop" in user["inventory"]:
            remove = "low budget laptop"
            break_laptop = random.randint(1, 100) <= 20 and user["money"] > 750
        else:
            await ctx.send(random.choice([f"{ctx.author.mention} what do you think you're gonna work with? Buy a laptop.", f"{ctx.author.mention} you don't have a laptop. Buy one.", f"{ctx.author.mention} buy a laptop to work."]))
            date = datetime.datetime.now().replace(microsecond=0)
            collection.update_one({"_id": ctx.author.id},
                                  {"$set": {"last_work": str(date)}})
            return

        if "good wifi router" in user["inventory"]:
            remove_router = "good wifi router"
            break_router = random.randint(1, 100) <= 10 and user["money"] > 15000
        elif "very fast wifi router" in user["inventory"]:
            remove_router = "very fast wifi router"
            break_router = random.randint(1, 100) <= 4 and user["money"] > 4000
        else:
            break_router = False

        if break_laptop and break_router:
            await ctx.send(f"{ctx.author.mention} your laptop and wifi router just broke! You can't work until you buy a new laptop.")
            inventory = user["inventory"]
            inventory.remove(remove)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            date = datetime.datetime.now().replace(microsecond=0)
            collection.update_one({"_id": ctx.author.id},
                                  {"$set": {"last_work": str(date)}})
            inventory = user["inventory"]
            # noinspection PyUnboundLocalVariable
            inventory.remove(remove_router)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            return
        elif break_router:
            await ctx.send(f"{ctx.author.mention} your wifi router just broke!")
            inventory = user["inventory"]
            # noinspection PyUnboundLocalVariable
            inventory.remove(remove_router)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
        elif break_laptop:
            await ctx.send(f"{ctx.author.mention} your laptop just broke! You can't work until you buy a new one.")
            inventory = user["inventory"]
            inventory.remove(remove)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            date = datetime.datetime.now().replace(microsecond=0)
            collection.update_one({"_id": ctx.author.id},
                                  {"$set": {"last_work": str(date)}})
            return

        if "antivirus" not in user["inventory"] and random.randint(1, 100) <= 10 and user["money"] > 500:
            msg = random.choice(["When will you buy that antivirus?", "You should buy an antivirus.", "Buy an antivirus to prevent this."])
            await ctx.send(f"**VIRUS!**\n{ctx.author.name} you just lost $250 because of a virus. {msg}")
            collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 250}})
        try:
            if user["antivirus_work"] >= 12 and "antivirus" in user["inventory"]:
                await ctx.send(f"**{ctx.author.name} your antivirus just expired, you should buy it again.**")
                inventory = user["inventory"]
                inventory.remove("antivirus")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
        except KeyError:
            collection.update_one({"_id": ctx.author.id}, {"$set": {"antivirus_work": 1}})

        if random.randint(1, 100) <= 20:
            inventory = user["inventory"]
            if user['job'] in jobs1:
                part = random.choice(parts1)
                inventory.append(part)
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                emoji = item_emoji(part)
                await ctx.send(random.choice([f"You accidentally found a **{emoji} {part}**.",
                                              f"You stole a **{emoji} {part}** from the storage.",
                                              f"You saw a **{emoji} {part}** and just took it.",
                                              f"You came upon a **{emoji} {part}** and took it."]))
            elif user['job'] in jobs2:
                part = random.choice(["cable", "fan", "hard disk", "ram", "cpu", "motherboard", "graphics card", "psu"])
                inventory.append(part)
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                emoji = item_emoji(part)
                await ctx.send(random.choice([f"You accidentally found a **{emoji} {part}**.",
                                              f"You stole a **{emoji} {part}** from the storage.",
                                              f"You saw a **{emoji} {part}** and just took it.",
                                              f"You came upon a **{emoji} {part}** and took it."]))
            elif user['job'] in jobs3:
                part = random.choice(["cable", "fan", "hard disk", "ram", "cpu", "motherboard", "graphics card", "water cooler tank", "water cooler pipe", "ssd", "psu"])
                inventory.append(part)
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                emoji = item_emoji(part)
                await ctx.send(random.choice([f"You accidentally found a **{emoji} {part}**.",
                                              f"You stole a **{emoji} {part}** from the storage.",
                                              f"You saw a **{emoji} {part}** and just took it.",
                                              f"You came upon a **{emoji} {part}** and took it."]))
            elif user['job'] in jobs4:
                part = random.choice(["cable", "fan", "hard disk", "ram", "cpu", "motherboard", "graphics card", "water cooler tank", "water cooler pipe", "ssd", "apple", "psu"])
                inventory.append(part)
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                emoji = item_emoji(part)
                await ctx.send(random.choice([f"You accidentally found a **{emoji} {part}**.",
                                              f"You stole a **{emoji} {part}** from the storage.",
                                              f"You saw a **{emoji} {part}** and just took it.",
                                              f"You came upon a **{emoji} {part}** and took it."]))

        new_money = user['money'] + payout
        if ctx.channel.id != 831462745316392990:
            level_bonus = random.randint(1, 100) >= 40
        else:
            level_bonus = False
        try:
            if "antivirus" in user["inventory"]:
                collection.update_one({"_id": ctx.author.id}, {"$set": {"antivirus_work": user["antivirus_work"] + 1}})
        except KeyError:
            pass
        if level_bonus:  # Check level bonus
            collection.update_one({"_id": ctx.author.id}, {"$set": {"money": new_money}})
            level = user['level']
            new_level = round(float(level) + 0.1, 1)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
            if str(new_level)[-1:] == "0":  # Check level up
                if int(str(new_level)[:-2]) == 3:  # Level up and new job
                    new_job = random.choice(jobs1)
                    await ctx.send(f"{ctx.author.mention} You worked and earned **${payout}**.\n**LEVEL UP, you are now level {str(new_level)[:-2]} and work as a {new_job}!**")
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"job": new_job}})
                elif int(str(new_level)[:-2]) == 7:
                    new_job = random.choice(jobs2)
                    await ctx.send(f"{ctx.author.mention} You worked and earned **${payout}**.\n**LEVEL UP, you are now level {str(new_level)[:-2]} and work as a {new_job}!**")
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"job": new_job}})
                elif int(str(new_level)[:-2]) == 15:
                    new_job = random.choice(jobs3)
                    await ctx.send(f"{ctx.author.mention} You worked and earned **${payout}**.\n**LEVEL UP, you are now level {str(new_level)[:-2]} and work as a {new_job}!**")
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"job": new_job}})
                elif int(str(new_level)[:-2]) == 25:
                    new_job = random.choice(jobs4)
                    await ctx.send(f"{ctx.author.mention} You worked and earned **${payout}**.\n**LEVEL UP, you are now level {str(new_level)[:-2]} and work as a {new_job}!**")
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"job": new_job}})
                else:  # Level up
                    await ctx.send(
                        f"{ctx.author.mention} You worked and earned **${payout}**.\n**LEVEL UP, you are now level {str(new_level)[:-2]}!**")
            else:  # No level up
                await ctx.send(f"{ctx.author.mention} You worked and earned **${payout}**.")
        else:  # No level bonus
            await ctx.send(f"{ctx.author.mention} You worked and earned **${payout}**.")
            collection.update_one({"_id": ctx.author.id}, {"$set": {"money": new_money}})

    @commands.command()
    async def sell(self, ctx, *item):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        item = " ".join(item).lower()
        if item == "graphic card":
            item = "graphics card"
        elif item == "mother board" or item == "main board" or item == "mainboard":
            item = "motherboard"
        elif item == "processor":
            item = "cpu"
        elif item == "tank" or item == "cooler tank":
            item = "water cooler tank"
        elif item == "pipe" or item == "cooler pipe":
            item = "water cooler pipe"
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        if item == "":
            await ctx.send("Specify the item you want to sell. Example: `sell cable`")
        elif item not in parts1 and item not in parts2 and item not in parts3:
            await ctx.send("That item is not on the market.")
        elif item not in user["inventory"]:
            await ctx.send(random.choice(["You don't have that.", "You don't own that."]))
        else:
            inventory = user["inventory"]
            if item == "cable":
                price = random.randint(50, 75)
                inventory.remove("cable")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "fan":
                price = fan_price
                inventory.remove("fan")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "hard disk" or item == "harddisk":
                price = harddisk_price
                inventory.remove("hard disk")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "ram":
                price = ram_price
                inventory.remove("ram")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "cpu":
                price = cpu_price
                inventory.remove("cpu")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "motherboard":
                price = motherboard_price
                inventory.remove("motherboard")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "graphics card":
                price = graphicscard_price
                inventory.remove("graphics card")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "ssd":
                price = ssd_price
                inventory.remove("ssd")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "water cooler tank":
                price = tank_price
                inventory.remove("water cooler tank")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "water cooler pipe":
                price = pipe_price
                inventory.remove("water cooler pipe")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            elif item == "psu" or item == "power":
                price = psu_price
                inventory.remove("psu")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
            else:
                await ctx.send("Something went wrong.")
                return

            emoji = item_emoji(item)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + price}})
            await ctx.send(f"You sold your **{emoji} {item}** for **${price}**.")

    @commands.command()
    async def startcompany(self, ctx, name=None):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        try:
            company = user["company"]
            if company:
                await ctx.send(f"{ctx.author.name} you already have a company. If you want to start a new company use `shutdowncompany`")
                return
        except KeyError:
            if user["job"] != "Not hired":
                await ctx.send("You have to quit your current job to start a company with `quit`. (you can always find a new job)")
                return
            if float(user["level"]) < 7:
                await ctx.send("You need to be atleast level **7**.")
                return
            if name is None:
                await ctx.send("You must pick a name for the company.\nExample: `startcompany google`")
            else:
                collection.update_one({"_id": ctx.author.id}, {"$set": {"company": {"name": name, "workers": 0, "building": "None"}}})
                collection.update_one({"_id": ctx.author.id}, {"$set": {"job": "Company Owner"}})
                await ctx.send(f"{ctx.author.mention} you have started a tech company called **{name}**. Grow your business by hiring workers, advertising and buying better equipment.\nFor more information use `help company`")

    @commands.command()
    async def shutdowncompany(self, ctx):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        msg = await ctx.send(f":exclamation: {ctx.author.mention} are you sure you want to do this? Your company will be lost forever.")
        emojis = ["✅", "❌"]
        for emoji in emojis:
            await msg.add_reaction(emoji)
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return

        def check(react, react_user):
            return react_user == ctx.author and str(react.emoji) == "✅" or react_user == ctx.author and str(react.emoji) == "❌"

        try:
            reaction, reaction_user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            if reaction.emoji == "✅":
                await ctx.send(f"**{user['company']['name']}** was shutdown by {ctx.author.name}.")
                collection.update_one({"_id": ctx.author.id}, {"$unset": {"company": ""}})
                collection.update_one({"_id": ctx.author.id}, {"$set": {"job": "Not hired"}})
            elif reaction.emoji == "❌":
                await ctx.send("Ok, you still have your company.")
        except asyncio.TimeoutError:
            pass

    @commands.command()
    async def company(self, ctx):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        try:
            user["company"]
        except KeyError:
            await ctx.send("You don't have a company. Start one with `startcompany`")
            return
        embed = discord.Embed(title=f"**{ctx.author.name}'s company**", description=f"Name: **{user['company']['name']}**\n\nBuilding: **{user['company']['building']}**\nWorkers: **{user['company']['workers']}**ㅤㅤㅤㅤㅤㅤ", color=discord.Color.dark_blue())
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        inventory = user["inventory"]
        i = 0
        laptops = f""
        for item in inventory:
            if item == "low budget laptop":
                emoji = ":keyboard: "
            elif item == "average laptop":
                emoji = ":computer: "
            elif item == "high quality laptop":
                emoji = ":desktop: "
            else:
                continue
            fl = item[0].upper()
            item = fl + item[1:]
            laptops = f"{laptops}\n{emoji}**{item}**"
            i += 1
        wifi = f""
        i = 0
        for item in inventory:
            if item == "slow wifi router":
                emoji = ":radio: "
            elif item == "good wifi router":
                emoji = ":fax: "
            elif item == "very fast wifi router":
                emoji = ":satellite: "
            else:
                continue
            fl = item[0].upper()
            item = fl + item[1:]
            wifi = f"{wifi}\n{emoji}**{item}**"
            i += 1
        other = f""
        i = 0
        apple_found = cable_found = fan_found = ssd_found = harddisk_found = pipe_found = tank_found = graphicscard_found = psu_found = ram_found = cpu_found = motherboard_found = False
        for item in inventory:
            if item == "antivirus":
                emoji = ":microbe: "
            elif item == "firewall":
                emoji = ":shield: "
            elif item == "apple" and not apple_found:
                apple_found = True
                amount = 0
                for thing in inventory:
                    if thing == "apple":
                        amount += 1
                if amount > 1:
                    emoji = f":apple: {amount} "
                    item = item + "'s"
                else:
                    emoji = ":apple: "
            else:
                continue
            fl = item[0].upper()
            item = fl + item[1:]
            other = f"{other}\n**{emoji}{item}**"
            i += 1

        parts = ""
        for item in inventory:
            if item == "cable" and not cable_found:
                cable_found = True
                amount = 0
                for thing in inventory:
                    if thing == "cable":
                        amount += 1
                if amount > 1:
                    emoji = f"<:powerplug:831458832013590569> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:powerplug:831458832013590569> "
            elif item == "fan" and not fan_found:
                fan_found = True
                amount = 0
                for thing in inventory:
                    if thing == "fan":
                        amount += 1
                if amount > 1:
                    emoji = f"<:fan:831458831690760192> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:fan:831458831690760192> "
            elif item == "hard disk" and not harddisk_found:
                harddisk_found = True
                amount = 0
                for thing in inventory:
                    if thing == "hard disk":
                        amount += 1
                if amount > 1:
                    emoji = f"<:harddisk:831458831786573834> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:harddisk:831458831786573834> "
            elif item == "psu" and not psu_found:
                psu_found = True
                amount = 0
                for thing in inventory:
                    if thing == "psu":
                        amount += 1
                if amount > 1:
                    emoji = f"<:power:831458832001138728> {amount} "
                    item = item + "'s"
                else:
                    emoji = f"<:power:831458832001138728> "
            elif item == "ram" and not ram_found:
                ram_found = True
                amount = 0
                for thing in inventory:
                    if thing == "ram":
                        amount += 1
                if amount > 1:
                    emoji = f"<:ram_1:831458832064446465> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:ram_1:831458832064446465> "
            elif item == "cpu" and not cpu_found:
                cpu_found = True
                amount = 0
                for thing in inventory:
                    if thing == "cpu":
                        amount += 1
                if amount > 1:
                    emoji = f"<:cpu:831458831388770335> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:cpu:831458831388770335> "
            elif item == "motherboard" and not motherboard_found:
                motherboard_found = True
                amount = 0
                for thing in inventory:
                    if thing == "motherboard":
                        amount += 1
                if amount > 1:
                    emoji = f"<:motherboard:831458831811870720> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:motherboard:831458831811870720> "
            elif item == "graphics card" and not graphicscard_found:
                graphicscard_found = True
                amount = 0
                for thing in inventory:
                    if thing == "graphics card":
                        amount += 1
                if amount > 1:
                    emoji = f"<:graphicscard:831458831493890079> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:graphicscard:831458831493890079> "
            elif item == "ssd" and not ssd_found:
                ssd_found = True
                amount = 0
                for thing in inventory:
                    if thing == "ssd":
                        amount += 1
                if amount > 1:
                    emoji = f"<:ssd:831458832244146196> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:ssd:831458832244146196>"
            elif item == "water cooler tank" and not tank_found:
                tank_found = True
                amount = 0
                for thing in inventory:
                    if thing == "water cooler tank":
                        amount += 1
                if amount > 1:
                    emoji = f"<:tank:831458832131686411> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:tank:831458832131686411> "
            elif item == "water cooler pipe" and not pipe_found:
                pipe_found = True
                amount = 0
                for thing in inventory:
                    if thing == "water cooler pipe":
                        amount += 1
                if amount > 1:
                    emoji = f"<:pipe:831458831900999690> {amount} "
                    item = item + "'s"
                else:
                    emoji = "<:pipe:831458831900999690> "
            else:
                continue
            fl = item[0].upper()
            item = fl + item[1:]
            parts = f"{parts}\n**{emoji}{item}**"
            i += 1
        em = discord.Embed(title=f"{ctx.author.name}s inventory", description=f"Laptops:{laptops}\n\nWifi router:{wifi}\n\nParts:{parts}\n\nOther:{other}",
                           color=discord.Colour.blue())
        await ctx.send(embed=em)

    @commands.command()
    async def use(self, ctx, item):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        inventory = user["inventory"]
        if item.lower() == "apple":
            if "apple" in inventory:
                amount = 0
                for thing in inventory:
                    if thing == "apple":
                        amount += 1
                level = user["level"]
                if amount > 1:
                    await ctx.send(f"How many apples do you want to eat? You have {amount} apples.")

                    def check(msg):
                        return msg.author == ctx.author and msg.channel == ctx.channel

                    try:
                        msg = await self.bot.wait_for("message", check=check, timeout=10)
                        if msg.content not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                            await ctx.send("That's not a correct number. Minimum is 1 and maximum is 10.")
                            return
                        else:
                            if amount <= int(msg.content):
                                await ctx.send("You don't have that many apples.")
                                return
                            i = 1
                            found = 0
                            for item in inventory:
                                if item == "apple" and found <= amount:
                                    print("Item: " + inventory[i])
                                    del inventory[i]
                                    level = float(level) + 1.0
                                    collection.update_one({"_id": ctx.author.id},
                                                          {"$set": {"level": str(level)}})
                                    collection.update_one({"_id": ctx.author.id},
                                                          {"$set": {"inventory": inventory}})
                                    found += 1
                                i += 1
                            if msg.content != "1":
                                await ctx.send(
                                    f"You ate {i} apples and leveled up! You are now level **{str(level)[:-2]}**")
                            else:
                                await ctx.send(
                                    f"You ate an apple and leveled up! You are now level **{str(level)[:-2]}**")
                    except asyncio.TimeoutError:
                        await ctx.send("You didn't reply...")
                        return
                elif amount == 1:
                    level = float(level) + 1.0
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(level)}})
                    inventory = user["inventory"]
                    inventory.remove("apple")
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                    await ctx.send(f"You ate an apple and leveled up! You are now level **{str(level)[:-2]}**")
                else:
                    await ctx.send("Invalid number.")
                    return
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
            else:
                await ctx.send("You don't have that item.")

    @commands.command()
    async def shop(self, ctx, page=None):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        if page == "1" or page == "one" or page == "first" or page is None:
            em = discord.Embed(title="Shop", description=":keyboard: **Low budget laptop `$750`**\nBasic laptop for freelancers, slow and easily breaks.\n\n:computer: **Average laptop `$2000`**\nWorks alright, medium speed and doesn't break often.\n\n:desktop: **High quality laptop `$4500`**\nThe fastest, hardly breaks.\n\n:fax: **Good wifi router `$1500`**\nMedium speed, will get the job done faster.\n\n:satellite: **Very fast wifi router `$4000`**\nLightning fast, almost never lags.\n\n:microbe: **Antivirus `$500`**\nProtect your money from viruses that can randomly steal. Expires after working 12 times.\n\n:shield: **Firewall `$750`**\nProtect your money from hackers. Expires after working 5 times.", color=discord.Colour.green())
            em.set_footer(text="py buy {item} to purchase ─ Page 1 of 3")
            await ctx.send(embed=em)
        elif page == "2" or page == "two" or page == "second":
            em = discord.Embed(title="Company shop", description=":house_abandoned: **Old building `$5000`**\nPretty old, but useful. Maximum of __3 workers__.\n\n<:building:829326857135718411> **Medium office building `$10000`**\nGood work environment. Maximum of __7 workers__.\n\n:office: **Large office building `$17500`**\nA lot of space. Also looks good. Maximum of __15 workers__.\n\n<:skyscraper:829330045469327411> **Skyscraper `$30000`**\nKinda expensive but has a lot of space. Maximum of __25 workers__.\n\n", color=discord.Colour.green())
            em.set_footer(text="py buy {item} to purchase ─ Page 2 of 3")
            await ctx.send(embed=em)
        elif page == "3" or page == "three" or page == "third":
            em = discord.Embed(title="Shop", description=":apple: **Apple** `$10000`\nEat this apple to instantly level up!", color=discord.Colour.green())
            em.set_footer(text="py buy {item} to purchase ─ Page 3 of 3")
            await ctx.send(embed=em)
        elif page is not None:
            await ctx.send(f"There is no shop page {page}")
        else:
            await ctx.send(f"There is no such shop page")

    @commands.command()
    async def buy(self, ctx, *, item=None):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        if item is None:
            await ctx.send("What do you want to buy? Include it in the command.")
            return
        inventory = user["inventory"]
        if "low budget laptop" in item.lower():
            if "low budget laptop" in user["inventory"]:
                await ctx.send(f"{ctx.author.mention} you already have that.")
                return
            if user["money"] >= 750:
                em = discord.Embed(title="Low budget laptop purchase", description=f"{ctx.author.mention} bought **low budget laptop** for `$750`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("low budget laptop")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 750}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money to buy that.", f"{ctx.author.mention} you can't afford that."]))
        elif "average laptop" in item.lower():
            if "average laptop" in user["inventory"]:
                await ctx.send(f"{ctx.author.mention} you already have that.")
                return
            if user["money"] >= 2000:
                em = discord.Embed(title="Average laptop purchase", description=f"{ctx.author.mention} bought **average laptop** for `$2000`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("average laptop")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 2000}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money to buy that.", f"{ctx.author.mention} you can't afford that."]))
        elif "high quality laptop" in item.lower():
            if "high quality laptop" in user["inventory"]:
                await ctx.send(f"{ctx.author.mention} you already have that.")
                return
            if user["money"] >= 4500:
                em = discord.Embed(title="High quality laptop purchase", description=f"{ctx.author.mention} bought **high quality laptop** for `$4500`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("high quality laptop")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 4500}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money to buy that.", f"{ctx.author.mention} you can't afford that."]))
        elif "good wifi" in item.lower():
            if "good wifi router" in user["inventory"]:
                await ctx.send(f"{ctx.author.mention} you already have that.")
                return
            if "very fast wifi router" in user["inventory"]:
                await ctx.send(random.choice(["Why would you want to buy slower wifi??", "You have better wifi, you don't need this.", "You already have better wifi."]))
                return
            if user["money"] >= 1500:
                em = discord.Embed(title="Good wifi router purchase", description=f"{ctx.author.mention} bought **good wifi router** for `$1500`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("good wifi router")
                inventory.remove("slow wifi router")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 1500}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money to buy that.", f"{ctx.author.mention} you can't afford that."]))
        elif "very fast wifi router" in item.lower() or "fast wifi router" in item.lower():
            if "very fast wifi router" in user["inventory"]:
                await ctx.send(f"{ctx.author.mention} you already have that.")
                return
            if user["money"] >= 4000:
                em = discord.Embed(title="Very fast wifi router purchase", description=f"{ctx.author.mention} bought **very fast wifi router** for `$4000`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("very fast wifi router")
                if "slow wifi router" in user["inventory"]:
                    inventory.remove("slow wifi router")
                elif "good wifi router" in user["inventory"]:
                    inventory.remove("good wifi router")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 4000}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money to buy that.", f"{ctx.author.mention} you can't afford that."]))
        elif "antivirus" in item.lower() or "anti virus" in item.lower() or "anti-virus" in item.lower():
            if "antivirus" in user["inventory"]:
                await ctx.send(f"{ctx.author.mention} you already have that.")
                return
            if user["money"] >= 500:
                em = discord.Embed(title="Antivirus purchase", description=f"{ctx.author.mention} bought **antivirus** for `$500`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("antivirus")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                collection.update_one({"_id": ctx.author.id}, {"$set": {"antivirus_work": 1}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 500}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money to buy that.", f"{ctx.author.mention} you can't afford that."]))
        elif "firewall" in item.lower() or "fire wall" in item.lower() or "fire-wall" in item.lower():
            if "firewall" in user["inventory"]:
                await ctx.send(f"{ctx.author.mention} you already have that.")
                return
            if user["money"] >= 750:
                em = discord.Embed(title="Firewall purchase", description=f"{ctx.author.mention} bought **firewall** for `$750`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("firewall")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                collection.update_one({"_id": ctx.author.id}, {"$set": {"firewall_uses": 5}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 500}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money to buy that.", f"{ctx.author.mention} you can't afford that."]))
        elif "old building" in item.lower():
            try:
                company = user["company"]
            except KeyError:
                await ctx.send("You need to have a company to buy this.")
                return
            if "old building" in user["company"]["building"]:
                await ctx.send(f"{ctx.author.mention} your company already has that building.")
                return
            elif "medium office building" in user["company"]["building"] or "large office building" in user["company"]["building"] or "skyscraper" in user["company"]["building"]:
                await ctx.send(f"{ctx.author.mention} why would you want to buy a worse building? You already have a {user['company']['building']}.")
                return
            if user["money"] >= 5000:
                em = discord.Embed(title="Old building purchase", description=f"{ctx.author.mention} bought **old building** for `$5000`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                company["building"] = "old building"
                collection.update_one({"_id": ctx.author.id}, {"$set": {"company": company}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 5000}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money for that.", f"{ctx.author.mention} you can't afford it."]))
        elif "medium office building" in item.lower() or "medium building" in item.lower():
            try:
                company = user["company"]
            except KeyError:
                await ctx.send("You need to have a company to buy this.")
                return
            if "medium office building" in user["company"]["building"]:
                await ctx.send(f"{ctx.author.mention} your company already has that building.")
                return
            elif "large office building" in user["company"]["building"] or "skyscraper" in user["company"]["building"]:
                await ctx.send(f"{ctx.author.mention} why would you want to buy a worse building? You already have a {user['company']['building']}.")
                return
            if user["money"] >= 10000:
                em = discord.Embed(title="Medium office building purchase", description=f"{ctx.author.mention} bought **medium office building** for `$10000`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                company["building"] = "medium office building"
                collection.update_one({"_id": ctx.author.id}, {"$set": {"company": company}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 10000}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money for that.", f"{ctx.author.mention} you can't afford it."]))
        elif "large office building" in item.lower() or "large building" in item.lower():
            try:
                company = user["company"]
            except KeyError:
                await ctx.send("You need to have a company to buy this.")
                return
            if "large office building" in user["company"]["building"]:
                await ctx.send(f"{ctx.author.mention} your company already has that building.")
                return
            elif "skyscraper" in user["company"]["building"]:
                await ctx.send(f"{ctx.author.mention} why would you want to buy a worse building? You already have a {user['company']['building']}.")
                return
            if user["money"] >= 17500:
                em = discord.Embed(title="Large office building purchase", description=f"{ctx.author.mention} bought **large office building** for `$17500`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                company["building"] = "large office building"
                collection.update_one({"_id": ctx.author.id}, {"$set": {"company": company}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 17500}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money for that.", f"{ctx.author.mention} you can't afford it."]))
        elif "skyscraper" in item.lower() or "sky scraper" in item.lower() or "skyscrapper" in item.lower():
            try:
                company = user["company"]
            except KeyError:
                await ctx.send("You need to have a company to buy this.")
                return
            if "skyscraper" in user["company"]["building"]:
                await ctx.send(f"{ctx.author.mention} your company already has that building.")
                return
            if user["money"] >= 30000:
                em = discord.Embed(title="Skyscraper purchase", description=f"{ctx.author.mention} bought **skyscraper** for `$30000`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                company["building"] = "skyscraper"
                collection.update_one({"_id": ctx.author.id}, {"$set": {"company": company}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 30000}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money for that.", f"{ctx.author.mention} you can't afford it."]))
        elif "apple" in item.lower():
            if user["money"] >= 10000:
                em = discord.Embed(title="Apple purchase", description=f"{ctx.author.mention} bought **apple** for `$10000`", color=discord.Colour.from_rgb(255, 248, 0))
                em.set_author(name="", icon_url=ctx.author.avatar_url)
                inventory.append("apple")
                collection.update_one({"_id": ctx.author.id}, {"$set": {"inventory": inventory}})
                if random.randint(1, 100) < 60:
                    level = user['level']
                    new_level = round(float(level) + 0.1, 1)
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"level": str(new_level)}})
                if ctx.channel.id != 831462745316392990:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - 10000}})
                await ctx.send(embed=em)
            else:
                await ctx.send(random.choice([f"{ctx.author.mention} you don't have enough money for that.", f"{ctx.author.mention} you can't afford it."]))
        else:
            lst = ["low budget laptop", "average laptop", "high quality laptop", "apple", "antivirus", "firewall", "skyscraper", "large office building", "medium office building", "old building"]
            item = ctx.message.content
            match = difflib.get_close_matches(item, lst, n=1)

            if len(match) == 0:
                await ctx.send("That item is not in the shop.")
                return
            else:
                await ctx.send(f"Did you mean `buy {match[0]}`?")

    @commands.command()
    async def give(self, ctx, member: discord.Member, amount: int, *message):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        if float(user["level"]) < 3:
            await ctx.send("You must atleast level 3 to give money to others.")
            return

        if member.id == ctx.author.id:
            await ctx.send("You can't give money to yourself.")
            return

        user2 = collection.find_one({"_id": member.id})
        if user2 is None:
            await ctx.send("That user doesn't have a career.")
            return

        if amount > user["money"]:
            await ctx.send("You don't have that much money.")
            return

        if message == ():
            message = ""
        else:
            message = ' '.join(message)
        await ctx.send(f"You gave ${amount} to {member.name}.")
        collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - amount}})
        collection.update_one({"_id": member.id}, {"$set": {"money": user2["money"] + amount}})
        await member.send(f"**{ctx.author.name}#{ctx.author.discriminator}** just gave you ${amount}!\n{message}")

    @commands.command()
    async def hack(self, ctx, member: discord.Member):
        if guilds.find_one({"_id": ctx.guild.id})["economy_disabled"]:
            await ctx.send("Economy is disabled for this server.")
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        member_db = collection.find_one({"_id": member.id})
        if member.id == self.bot.user.id:
            await ctx.send("You can't hack me?! <:kek:832189648343531560>")
            return
        if member_db is None:
            await ctx.send("That user doesn't have a career.")
            return
        if ctx.author == member:
            await ctx.send("You can't hack yourself...")
            return
        if "average laptop" not in user["inventory"] and "high quality laptop" not in user["inventory"] and "low budget laptop" not in user["inventory"]:
            await ctx.send("You need to have laptop to hack, either average or high quality.")
            return
        elif "average laptop" not in user["inventory"] and "high quality laptop" not in user["inventory"]:
            await ctx.send("You can't hack with a low budget laptop.")
            return
        try:
            last_hack = datetime.datetime.strptime(user["last_hack"], "%Y-%m-%d %H:%M:%S")
            if last_hack <= datetime.datetime.now():
                date = datetime.datetime.now().replace(microsecond=0)
                date += datetime.timedelta(hours=6)
                collection.update_one({"_id": ctx.author.id}, {"$set": {"last_hack": str(date)}})

                ip = str(random.randint(100, 999))
                address = f"{ip}.{random.randint(1, 10)}.{random.randint(1, 10)}.{random.randint(1, 10)}"
                messages = ["<a:loading_pic:833966183841529916> Tracking IP address...",
                            f"<a:loading_pic:833966183841529916> IP address found: {address}",
                            f"<a:loading_pic:833966183841529916> Hacking {member.name}#{member.discriminator}...",
                            "<a:loading_pic:833966183841529916> Stealing money..."]
                msg = await ctx.send("Hack starting...")
                i = 0
                member_db = collection.find_one({"_id": member.id})
                for message in messages:
                    await msg.edit(content=message)
                    if i == 3 and "firewall" in member_db["inventory"]:
                        await asyncio.sleep(1)
                        await msg.edit(content=":anger: Firewall Found!")
                        firewall_found = True
                        await asyncio.sleep(1)
                        break
                    firewall_found = False
                    await asyncio.sleep(2)
                    i += 1
                payout = random.randint(750, 1500)
                if member_db["money"] - payout < 500:
                    await ctx.send("That user is too poor to be hacked.")
                else:
                    if firewall_found:
                        collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - payout}})
                        if member_db["firewall_uses"] == 0:
                            desc = f"{ctx.author.name}#{ctx.author.discriminator} tried to hack you but your firewall stopped him.\n**Your firewall expired**"
                            inventory = member_db["inventory"]
                            inventory.remove("firewall")
                            collection.update_one({"_id": member.id},
                                                  {"$set": {"inventory": inventory}})
                        else:
                            collection.update_one({"_id": member.id},
                                                  {"$set": {"firewall_uses": member_db["firewall_uses"] - 1}})
                            desc = f"{ctx.author.name}#{ctx.author.discriminator} tried to hack you but your firewall stopped him.\nRemaining firewall uses: {member_db['firewall_uses']}"
                        embed = discord.Embed(title="Hack attempt!",
                                              description=desc)
                        embed.set_author(icon_url=ctx.author.avatar_url, name="Hacker")
                        await msg.edit(content=":x: Hack failed!")
                        await ctx.send(f"You lost **${payout}** for trying to hack {member.name}#{member.discriminator}")
                        await member.send(embed=embed)
                    else:
                        collection.update_one({"_id": member.id}, {"$set": {"money": member_db["money"] - payout}})
                        collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + payout}})
                        embed = discord.Embed(title="You were hacked!",
                                              description=f"{ctx.author.name}#{ctx.author.discriminator} stole **${payout}** from you!\nYour remaining balance is ${member_db['money']}")
                        embed.set_author(icon_url=ctx.author.avatar_url, name="Hacker")
                        await msg.edit(content="<a:evil_tick:836521455008874546> Hack complete!")
                        await ctx.send(f"You stole **${payout}** from {member.name}#{member.discriminator}")
                        await member.send(embed=embed)
            else:
                duration = last_hack - datetime.datetime.now()
                seconds = duration.total_seconds()
                hours = round((seconds // 60) // 60)
                minutes = round((seconds // 60) % 60)
                seconds = round(seconds % 60)
                if hours == 0 and minutes == 0:
                    description = f"{ctx.author.mention} you must wait **{seconds} seconds** before hacking again."
                elif hours == 0:
                    description = f"{ctx.author.mention} you must wait **{minutes} minutes and {seconds} seconds** before hacking again."
                elif minutes == 0:
                    description = f"{ctx.author.mention} you must wait **{minutes} minutes and {seconds} seconds** before hacking again."
                else:
                    description = f"{ctx.author.mention} you must wait **{hours} hours, {minutes} minutes and {seconds} seconds** before hacking again."
                await ctx.send(description)
        except KeyError:
            date = datetime.datetime.now().replace(microsecond=0)
            date += datetime.timedelta(hours=6)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"last_hack": str(date)}})

            ip = str(random.randint(100, 999))
            address = f"{ip}.{random.randint(1, 10)}.{random.randint(1, 10)}.{random.randint(1, 10)}"
            messages = ["<a:loading_pic:833966183841529916> Tracking IP address...",
                        f"<a:loading_pic:833966183841529916> IP address found: {address}",
                        f"<a:loading_pic:833966183841529916> Hacking {member.name}#{member.discriminator}...",
                        "<a:loading_pic:833966183841529916> Stealing money..."]
            msg = await ctx.send("Hack starting...")
            i = 0
            member_db = collection.find_one({"_id": member.id})
            for message in messages:
                await msg.edit(content=message)
                if i == 3 and "firewall" in member_db["inventory"]:
                    await asyncio.sleep(1)
                    await msg.edit(content=":anger: Firewall Found!")
                    await asyncio.sleep(1)
                    firewall_found = True
                    break
                firewall_found = False
                await asyncio.sleep(2)
                i += 1

            payout = random.randint(750, 1500)
            if member_db["money"] - payout < 500:
                await msg.edit(':warning: Hack failed.')
                await ctx.send(f"{ctx.author.mention} {member.name}#{member.discriminator} is too poor to be hacked.")
            else:
                if firewall_found:
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] - payout}})
                    if member_db["firewall_uses"] == 0:
                        desc = f"{ctx.author.name}#{ctx.author.discriminator} tried to hack you but your firewall stopped him.\n**Your firewall expired**"
                        inventory = member_db["inventory"]
                        inventory.remove("firewall")
                        collection.update_one({"_id": member.id},
                                              {"$set": {"inventory": inventory}})
                    else:
                        collection.update_one({"_id": member.id},
                                              {"$set": {"firewall_uses": member_db["firewall_uses"] - 1}})
                        desc = f"{ctx.author.name}#{ctx.author.discriminator} tried to hack you but your firewall stopped him.\nRemaining firewall uses: {member_db['firewall_uses']}"
                    embed = discord.Embed(title="Hack attempt!",
                                          description=desc)
                    embed.set_author(icon_url=ctx.author.avatar_url, name="Hacker")
                    await msg.edit(content=":x: Hack failed!")
                    await ctx.send(f"You lost **${payout}** for trying to hack {member.name}#{member.discriminator}")
                    await member.send(embed=embed)
                else:
                    collection.update_one({"_id": member.id}, {"$set": {"money": member_db["money"] - payout}})
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + payout}})
                    embed = discord.Embed(title="You were hacked!",
                                          description=f"{ctx.author.name}#{ctx.author.discriminator} stole **${payout}** from you!\nYour remaining balance is ${member_db['money']}")
                    embed.set_author(icon_url=ctx.author.avatar_url, name="Hacker")
                    await msg.edit(content="<a:evil_tick:836521455008874546> Hack complete!")
                    await ctx.send(f"You stole **${payout}** from {member.name}#{member.discriminator}")
                    await member.send(embed=embed)

    @hack.error
    async def hack_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Who do you want to hack? Include the discord.Member in the command.")
            return
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            await ctx.send("Invalid member argument given. Mention a member or include his id.")
            return
        raise error

    @commands.command(aliases=["ranks", "rank", "lb", "leaderboards"])
    async def leaderboard(self, ctx, t=None):
        return
        msg = await ctx.send("<a:loading_pic:833966183841529916> Fetching Leaderboard...")
        users_levels = {}
        users_money = {}

        for user in u:
            member_exists = collection.find_one({"_id": user.id})
            users_levels[user.id] = round(float(member_exists["level"]))
            users_money[user.id] = member_exists["money"]
        if t == "-l" or t == "-level":
            users = {k: v for k, v in sorted(users_levels.items(), key=lambda item: item[1], reverse=True)}
        elif t in ["-c", "-m", "-b", "-balance", "-cash", "-money", "-bal"]:
            users = {k: v for k, v in sorted(users_money.items(), key=lambda item: item[1], reverse=True)}
        else:
            users = {k: v for k, v in sorted(users_levels.items(), key=lambda item: item[1], reverse=True)}
        rank = 1
        embed = discord.Embed(title="Server leaderboard | Top 10", description="", colour=discord.Color.green())
        for x in users:
            if ctx.author.id != x:
                user = self.bot.get_user(x) or await self.bot.fetch_user(x)
                embed.add_field(name=f"{rank}. {user.name}#{user.discriminator}",
                                value=f"Level: `{users_levels[x]}` • Money: ${users_money[x]}", inline=False)
            else:
                user_rank = rank
                embed.add_field(name=f"{rank}. {ctx.author.name}#{ctx.author.discriminator}",
                                value=f"Level: `{users_levels[x]}` • Money: ${users_money[x]}", inline=False)
            rank += 1
        try:
            if user_rank == 1:
                rank_text = f"Your rank: {user_rank}st"
            elif user_rank == 2:
                rank_text = f"Your rank: {user_rank}nd"
            else:
                rank_text = f"Your rank: {user_rank}th"
                embed.set_footer(text=rank_text)
        except UnboundLocalError:
            pass
        await msg.delete()
        await ctx.send(embed=embed)

    @build.error
    async def build_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Specify the device you want to build. Example: `build computer`")

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            await ctx.send("You must specify a discord.Member object and an amount as an integer. `give @SomeGuy 100` or `give 123456789 100`\nYou can also add a message at the end: `give @Carl 150 take some money!`")
            return

    @use.error
    async def use_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("What do you want to use?")
            return

    @career.error
    async def career_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound) or isinstance(error, commands.BadArgument):
            await ctx.author.send("Invalid member type given, you must mention a member or give his id.")
            return
        raise error

    @toggleeconomy.error
    async def economy_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You are missing the `manage_messages` permission to use this command.")

def setup(bot):
    bot.add_cog(Economy(bot))
