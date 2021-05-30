from discord.ext import commands
import datetime
import discord
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from discord_slash import cog_ext, SlashContext

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['users']

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="daily", description="Claim a daily reward of 800$")
    async def daily(self, ctx: SlashContext):
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        try:
            last_daily = datetime.datetime.strptime(user["last_daily"], "%Y-%m-%d %H:%M:%S")
            if last_daily <= datetime.datetime.now():
                date = datetime.datetime.now().replace(microsecond=0)
                date += datetime.timedelta(days=1)
                collection.update_one({"_id": ctx.author.id}, {"$set": {"last_daily": str(date)}})
                collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + 800}})
                em = discord.Embed(title=f"Daily Reward for {ctx.author.name}", description=f"**$800** was placed in {ctx.author.name}'s account", color=discord.Colour.blue())
                em.timestamp = datetime.datetime.utcnow()
                await ctx.send(embed=em)
            else:
                duration = last_daily - datetime.datetime.now()
                seconds = duration.total_seconds()
                hours = round((seconds // 60) // 60)
                minutes = round((seconds // 60) % 60)
                seconds = round(seconds % 60)
                if hours == 0 and minutes == 0:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{seconds} seconds.**"
                elif hours == 0:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{minutes} minutes and {seconds} seconds.**"
                elif minutes == 0:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{hours} hours and {seconds} seconds.**"
                else:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{hours} hours, {minutes} minutes and {seconds} seconds.**"
                em = discord.Embed(title="Daily reward cooldown",
                                   description=description,
                                   colour=discord.Colour.dark_red())
                await ctx.send(embed=em)
        except KeyError:
            date = datetime.datetime.now().replace(microsecond=0)
            date += datetime.timedelta(days=1)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"last_daily": str(date)}})
            collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + 800}})
            em = discord.Embed(title=f"Daily Reward for {ctx.author.name}",
                               description=f"**$800** was placed in {ctx.author.name}'s account", color=discord.Colour.blue())
            em.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=em)
            return


    @commands.command()
    async def daily(self, ctx):
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.send("You must have a career, use `startcareer`")
            return
        try:
            last_daily = datetime.datetime.strptime(user["last_daily"], "%Y-%m-%d %H:%M:%S")
            if last_daily <= datetime.datetime.now():
                date = datetime.datetime.now().replace(microsecond=0)
                date += datetime.timedelta(days=1)
                collection.update_one({"_id": ctx.author.id}, {"$set": {"last_daily": str(date)}})
                collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + 800}})
                em = discord.Embed(title=f"Daily Reward for {ctx.author.name}", description=f"**$800** was placed in {ctx.author.name}'s account", color=discord.Colour.blue())
                em.timestamp = datetime.datetime.utcnow()
                await ctx.send(embed=em)
            else:
                duration = last_daily - datetime.datetime.now()
                seconds = duration.total_seconds()
                hours = round((seconds // 60) // 60)
                minutes = round((seconds // 60) % 60)
                seconds = round(seconds % 60)
                if hours == 0 and minutes == 0:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{seconds} seconds.**"
                elif hours == 0:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{minutes} minutes and {seconds} seconds.**"
                elif minutes == 0:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{hours} hours and {seconds} seconds.**"
                else:
                    description = f"{ctx.author.mention} you already claimed your reward.\n\n You can claim it again in **{hours} hours, {minutes} minutes and {seconds} seconds.**"
                em = discord.Embed(title="Daily reward cooldown",
                                   description=description,
                                   colour=discord.Colour.dark_red())
                await ctx.send(embed=em)
        except KeyError:
            date = datetime.datetime.now().replace(microsecond=0)
            date += datetime.timedelta(days=1)
            collection.update_one({"_id": ctx.author.id}, {"$set": {"last_daily": str(date)}})
            collection.update_one({"_id": ctx.author.id}, {"$set": {"money": user["money"] + 800}})
            em = discord.Embed(title=f"Daily Reward for {ctx.author.name}",
                               description=f"**$800** was placed in {ctx.author.name}'s account", color=discord.Colour.blue())
            em.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=em)
            return

def setup(bot):
    bot.add_cog(Daily(bot))
