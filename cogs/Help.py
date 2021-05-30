import os
import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['guilds']
users = db['users']

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_prefix(self, message):
        if not message.guild:
            return
        id = message.guild.id
        pref = collection.find_one({"_id": id})
        post = {"_id": id, "prefix": ["py ", "PY ", "Py ", "pY "]}
        if pref is None:
            collection.insert_one(post)
            return ["py ", "PY ", "Py ", "pY "]
        else:
            return pref['prefix']

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            embed_var = discord.Embed(title="Help",
                                      description=":money_with_wings: **Economy**\n`career`, `work`, `shop`, `buy`, `sell`, `hack`, `inventory`, `give`, `daily`, `startcareer`, `quit`, `company`, `startcompany`, `shutdowncompany`\nDetailed: `py help economy`\n\n:snake: **Python**\n`eval`, `docs`, `tutorials`, `error`, `pypi`, `info`, `codechannel`\n\n:gear: **Config**\n`toggleeconomy`, `changeprefix`, `defaultprefix`\n\n:newspaper: **Other**\n`suggest`, `about`, `invite`, `ping`\n\nFor information about each command use `py help {command}`",
                                      color=int("0x36393f", 16))
            await ctx.send(embed=embed_var)
        elif ctx.invoked_subcommand not in ["economy", "eval", "toggleeconomy", "evaluation", "codechannel", "tutorials", "pypi", "error", "ping", "changeprefix", "defaultprefix", "about", "info", "suggest", "docs"]:
            embed_var = discord.Embed(title="Command not found",
                                      description=":x:   Make sure that the command exists and that you spelled it right.",
                                      color=int("0x36393f", 16))
            await ctx.send(embed=embed_var)

    @help.command()
    async def economy(self, ctx):
        embed_var = discord.Embed(title="Economy",
                                  description=f"Start a career with `py startcareer`.\n\nEarn money by working and leveling up.\nAt levels `3`, `7`, `15` and `25` you will get a better job.\nYour working payout depends on your job. You need to have a laptop to work. Laptops have a small chance to break, a wifi router will reduce the work cooldown.\n\nWhen you reach level 7, you can start a company that can grow big and earn you even more money than a normal job.\n\nVote for the bot on **[top.gg](https://top.gg/bot/800832309989081118/vote)** to get a reward of **$1000**\n\n**Commands:**\n`daily` - claim a reward of $800 every 24 hours\n`career` - see your balance, job and level\n`work` - earn money\n`shop` - buy better equipment\n`buy` - from the shop\n`sell` - your items\n`hack` - steal other users money\n`use` - use an item you bought\n`give` - send money to other members\n`inventory` - see what items you own\n`startcareer`\n`retire` - delete your career data\n`startcompany`\n`shutdowncompany`\n`company`\n\nUsers playing: {users.find({}).count()}",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command(aliases=["evaluation"])
    async def eval(self, ctx):
        embed_var = discord.Embed(title="Eval Command",
                                  description="Execute python code and get the output.\n The code is sandboxed by removing specific modules and keywords.\n\nCorrect usage: `py eval <code here>`",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def toggleeconomy(self, ctx):
        embed_var = discord.Embed(title="Toggle Economy Command",
                                  description="Disable or enable economy for this guild.\n\nEnable - `toggleeconomy on`\nDisable - `toggleeconomy off`",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def codechannel(self, ctx):
        embed_var = discord.Embed(title="Code channel Command",
                                  description="Start a coding channel with `cc init`\n\nWhen you did, anyone can just send something in that channel and it will be added to the code in the bots messsage.\n`cc` is a shortcut for `codechannel` but you can use any of those.\n`cc delete` will delete an amount of last lines in the code.\n`cc status` shows if the coding channel is receiving messages. Use `cc start` or `cc stop` to change it.\n\nCommands: `cc init`, `cc delete`, `cc status`, `cc start`, `cc stop`",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def tutorials(self, ctx):
        embed_var = discord.Embed(title="Tutorials Command",
                                  description="Learn about basic or intermediate things in python.\nYou can learn about variables, data types, loops and more or intermediate things like using json in python, datetime and more.\n\nYou can see definitions and examples of everything.\n\nAll information is from W3Schools.",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def pypi(self, ctx):
        embed_var = discord.Embed(title="PyPi Command",
                                  description="Get information about packages from [PyPi](https://pypi.org).\n\nCorrect usage: `py pypi <package>`",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def error(self, ctx):
        embed_var = discord.Embed(title="Error Command",
                                  description="It is used to get information about common python errors. \n You can use it by typing `py error syntax` for ex. \n \n There are **8** common errors you can get information about. \n `syntax` \n `index` \n `module` \n `key` \n `type` \n `value` \n `name` \n `unicode`",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def ping(self, ctx):
        embed_var = discord.Embed(title="Ping Command",
                                  description="Shows how much time the bot needs to respond (in milliseconds).",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def changeprefix(self, ctx):
         embed_var = discord.Embed(title="Changeprefix Command",
                                   description="Changes the bot prefix of the server. \n\n Correct usage: `py changeprefix <new prefix>`",
                                   color=int("0x36393f", 16))
         await ctx.send(embed=embed_var)

    @help.command()
    async def defaultprefix(self, ctx):
         embed_var = discord.Embed(title="Defaultprefix Command",
                                   description="Sets the default bot prefix of the server which is `py`. \n The default prefix is case insensitive. Custom prefixes set by `changeprefix` are not case insensitive.",
                                   color=int("0x36393f", 16))
         await ctx.send(embed=embed_var)

    @help.command()
    async def about(self, ctx):
        embed_var = discord.Embed(title="About Command",
                                  description="Python version that the bot uses, discord.py version, ping, host, amount of servers the bot is in and the amount of commands",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def info(self, ctx):
        embed_var = discord.Embed(title="Info Command",
                                  description="Links and info about python.",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def invite(self, ctx):
        embed_var = discord.Embed(title="Invite Command",
                                  description="Bot invite link, support server and the website link.",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command()
    async def suggest(self, ctx):
        embed_var = discord.Embed(title="Suggest Command",
                                  description="Make a suggestion for the bot, it can be a feature, issue or anything.",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command(aliases=["stackoverflow", "stack", "question"])
    async def questions(self, ctx):
        embed_var = discord.Embed(title="Discord Stackoverflow",
                                  description="You can create questions for help with your code or to ask something.\nBefore that you need to make a profile with `createprofile`\n\nIf you want to create a new question, go to <#841398524208873492>\n\nAnswering, commenting, marking answers as the solution and getting answers marked as the solution will give you points.\nAt certain amounts of points you will get a new rank and a role.\n\nTo comment a question use `py comment <text>`\nTo answer use `py answer <text>`\nIf you want to make someone answer as a solution you can react to with it :white_check_mark: or use `py solution <answer id>`\nTo close your question use `py delete`",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

    @help.command(aliases=['documentation', 'doc'])
    async def docs(self, ctx):
        embed_var = discord.Embed(title="Documentation Command",
                                  description="Get documentation links for python or discord.py.\n\nPython documentation: `py docs <name>`\nDiscord.py documentation: `py docs dpy <name>`\nThe name is what you want to get the link for.",
                                  color=int("0x36393f", 16))
        await ctx.send(embed=embed_var)

def setup(bot):
    bot.add_cog(Help(bot))
