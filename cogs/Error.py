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

class Error(commands.Cog):
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

    @commands.command()
    async def error(self, ctx, *args):
        for word in args:
            if word == "syntax":
                embed_var = discord.Embed(title="Syntax Error",
                                          description="Usually the easiest to spot, syntax errors occur when you make a __typo__. Not ending an if statement with the __colon__ is an example of an syntax error, as is __misspelling__ a Python keyword (e.g. using whille instead of while). Syntax error usually appear at compile time and are reported by the interpreter.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            elif word == "index":
                embed_var = discord.Embed(title="Index Error",
                                          description="Its one of the more basic and common exceptions found in Python, as it is raised whenever attempting to __access an index that is outside the bounds of a list__.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            elif word == "module":
                embed_var = discord.Embed(title="Module Not Found Error",
                                          description="Its raised when Python __cannot successfully import a module__. ... Because you __haven't installed__ the dependency, Python does not know where to locate it. ModuleNotFoundErrors come up in __user-defined modules__. Often, this error is caused by __importing files relatively__ when doing so is not allowed.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            elif word == "key":
                embed_var = discord.Embed(title="Key Error",
                                          description="Exception is raised when you try to access a key that __isn't in a dictionary__ ( dict ). Python's official documentation says that the KeyError is raised when a __mapping key is accessed__ and __isn't found in the mapping__. ... The most common mapping in Python is the dictionary.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            elif word == "type":
                embed_var = discord.Embed(title="Type Error",
                                          description="It occurs in Python when you attempt to call a function or use an operator on something of the __incorrect type__.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            elif word == "value":
                embed_var = discord.Embed(title="Value Error",
                                          description="A problem with the content of the object you __tried to assign the value to__. This is not to be confused with types in Python. For instance, imagine you have a dog and you try to put it in a fish tank. ... ValueError: int() cannot convert 'dog' into an integer.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            elif word == "name":
                embed_var = discord.Embed(title="Name Error",
                                          description="Its raised when you try to use a __variable or a function name that is not valid__. In Python, code runs from top to bottom. This means that you cannot declare a variable after you try to use it in your code. Python would not know what you wanted the variable to do.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            elif word == "unicode":
                embed_var = discord.Embed(title="Unicode Error",
                                          description="The key to troubleshooting Unicode errors in Python is to know what types you have. Then, __try these steps__: If some variables are byte sequences instead of Unicode objects, convert them to Unicode objects with **decode()** before handling them.",
                                          color=15105570)
                await ctx.send(embed=embed_var)
            else:
                embed_var = discord.Embed(title="Wrong command usage",
                                          description=":no_entry_sign: **Specify the correct type of error** when using the `error` command. For more information type `py help`. \n \n :x:  `py error` - no type of error in the end \n :x:  `py error blabla` - that error doesn't exist \n \n :white_check_mark:  `py error syntax` for ex.",
                                          color=15158332)
                await ctx.send(embed=embed_var)
                return
        if args == ():
            embed_var = discord.Embed(title="Wrong command usage",
                                      description=":no_entry_sign: **Specify the correct type of error** when using the `error` command. For more information type `py help`. \n \n :x:  `py error` - no type of error in the end \n :x:  `py error blabla` - that error doesn't exist \n \n :white_check_mark:  `py error syntax` for ex.",
                                      color=15158332)
            await ctx.send(embed=embed_var)

def setup(bot):
    bot.add_cog(Error(bot))
