from discord.ext import commands
import discord
from discord_components import Button, ButtonStyle
import asyncio
import signal
from sandbox import Sandbox
from discord.utils import escape_markdown
import aiohttp
import difflib
try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib
import zlib
import io
import re
import os

client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
# get a list of package names
packages = client.list_packages()

class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')

class python(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self._recently_blocked = set()

    @commands.command(help="Information about the programming language python.", description="This command takes no arguments.", usage="info")
    async def info(self, ctx):
        embed_var = discord.Embed(title="Python Info",
                                  description="> [**Official Python Site**](https://python.org) \n> [**About**](https://www.python.org/about/) \n> [**Downloads**](https://python.org/downloads) \n> [**Docs**](https://docs.python.org/) \n \n Latest version: [**DOWNLOAD 3.9.4**](https://www.python.org/downloads/release/python-394/)",
                                  color=15844367)
        await ctx.send(embed=embed_var)

    @commands.command(aliases=["e", "evaluation"], help="Run python code in discord.", description="code (Required): Code to run", usage="eval <code>")
    async def eval(self, ctx, *, code):
        async with ctx.typing():
            def handler(signum, frame):
                raise Exception("end of time")

            def run():
                return Sandbox.safe_exec(code)

            signal.signal(signal.SIGALRM, handler)

            signal.alarm(2)

            output = run()

            signal.alarm(0)

            try:
                emoji = self.bot.get_emoji(833349328277471282)
                message = await ctx.send(
                    f"{ctx.author.mention} {output}",
                    components=[
                        Button(style=ButtonStyle.gray, label=" ", emoji=emoji),
                    ]
                )
            except discord.HTTPException:
                message = await ctx.send(
                    f":warning: Your eval job has completed with return code 0.\n\n```[Too long message]             ```",
                    components=[
                        Button(style=ButtonStyle.gray, label=" ", emoji=emoji),
                    ]
                )

        try:
            res = await self.bot.wait_for('button_click', timeout=60)
            if res.message.id == message.id and res.user.id == ctx.author.id:
                await res.respond(
                    type=7,
                    content=f"{ctx.author.name}'s code evaluation was deleted."
                )
        except asyncio.TimeoutError:
            pass

    @eval.error
    async def eval_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Add the code you want to execute. Example: `eval print(2 - 2)`")

    @commands.command(aliases=("package", "pack"), help="Get a pypi package link.", description="package (Required): Package name", usage="pypi <package>")
    async def pypi(self, ctx, package):
        url = "https://pypi.org/pypi/{package}/json"
        embed = discord.Embed()
        icon_url = "https://cdn.discordapp.com/emojis/766274397257334814.png"
        embed.set_thumbnail(url=icon_url)
        embed.colour = discord.Colour.blue()

        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(package=package)) as resp:
                if str(resp.status) == "404":
                    match = difflib.get_close_matches(package, packages, n=1)

                    if len(match) == 0:
                        embed.description = "Package could not be found."
                    else:
                        embed.description = f"Package could not be found.\nDid you mean `{match[0]}?`"

                elif str(resp.status) == "200":
                    response_json = await resp.json()
                    info = response_json["info"]

                    embed.title = f"{info['name']} v{info['version']}"

                    embed.url = info["package_url"]

                    summary = escape_markdown(info["summary"])

                    # Summary could be completely empty, or just whitespace.
                    if summary and not summary.isspace():
                        embed.description = summary
                    else:
                        embed.description = "No summary provided."

                else:
                    embed.description = "There was an error when fetching your PyPi package."
                    print(f"Error when fetching PyPi package: {resp.text()}.")

        await ctx.send(embed=embed)

    @pypi.error
    async def pypi_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(":x: Missing the package name.")
            return

    @commands.command(aliases=["tutorial"], help="Python tutorials from W3Schools in discord.", description="tutorial (Optional): Category", usage="tutorial [category]")
    async def tutorials(self, ctx, *args):
        if args == ():
            embed = discord.Embed(title="Tutorials", description="**Basics**\nVariables, data types, operators, conditions, loops...\n\n**Intermediate**\nClasses, modules, dates, json...", colour=discord.Colour.teal())
            embed.set_footer(text="py tutorials {category}")
            await ctx.send(embed=embed)
        else:
            args = ' '.join(args).lower()
            if "basics" in args or "basic" in args:
                embed = discord.Embed(title="Basics", description="**Variables**\nContainers for storing data values.\n\n**Data Types**\nDifferent types and their categories.\n\n**Operators**\nPerform operations on variables.\n\n**Conditions**\nIf...Else\n\n**Loops**\nWhile, For...\n\n**Functions**\nBlock of code that runs when it is called", colour=discord.Colour.teal())
                embed.set_thumbnail(
                    url="https://opensource.com/sites/default/files/styles/image-full-size/public/lead-images/python_programming_question.png?itok=cOeJW-8r")
                embed.set_footer(text="py tutorials {category}")
                await ctx.send(embed=embed)
            elif "intermediate" in args or "intermiedate" in args:
                embed = discord.Embed(title="Intermediate", description="**Classes/Objects**\nObject constructor\n\n**Modules**\nCode libraries\n\n**Dates**\nDatetime module\n\n**JSON**\nStore and exchange small data", colour=discord.Colour.orange())
                embed.set_thumbnail(
                    url="https://assetsds.cdnedge.bluemix.net/sites/default/files/styles/amp_metadata_content_image_min_696px_wide/public/feature/images/3094291_0.jpg?itok=xnOEF_vP")
                embed.set_footer(text="py tutorials {category}")
                await ctx.send(embed=embed)
            elif "variables" in args or "variable" in args:
                embed = discord.Embed(title="Variables", description="Variables are containers for storing data values.\n Python has no command for declaring a variable. A variable is created the moment you first assign a value to it.\n\n**Example:**\n```x = 5\ny = 'John'```\n\nVariables do not need to be declared with any particular type, and can even change type after they have been set.", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "data" in args and "types" in args or "datatypes" in args or "data" and "type" in args:
                embed = discord.Embed(title="Data Types", description="In programming, data type is an important concept.\nVariables can store data of different types, and different types can do different things.\nPython has the following data types built-in by default, in these categories:\n\n**Text Type:** `str`\n**Numeric Types:** `int`, `float`, `complex`\n**Sequence Types:** `list`, `tuple`, `range`\n**Mapping Type:** `dict`\n**Set Types:** `set`, `frozenset`\n**Boolean Type:** `bool`\n\nYou can get the data type of any object by using the type() function\n\n**Example:**\n```x = 5\nprint(type(x))```", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "operators" in args or "operator" in args:
                embed = discord.Embed(title="Operators", description="Operators are used to perform operations on variables and values. In the example below, we use the + operator to add together two values\n\n**Example:**\n```print(10 + 5)```\n\n**Arithmetic operators**\nArithmetic operators are used with numeric values to perform common mathematical operations\n\n**Assignment operators**\nAssignment operators are used to assign values to variables\n\n**Comparison operators**\nComparison operators are used to compare two values\n\n**Logical operators**\nLogical operators are used to combine conditional statements\n\n**Identity Operators**\nIdentity operators are used to compare the objects, not if they are equal, but if they are actually the same object, with the same memory location\n\n**Membership operators**\nMembership operators are used to test if a sequence is presented in an object\n\nUse `tutorial operator {operator category}` for more info.", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "condition" in args or "conditions" in args:
                embed = discord.Embed(title="Conditions", description='**If statement**\nAn __if statement__ is written by using the `if` keyword.\n\n```\na = 33\nb = 200\nif b > a:\n   print("b is greater than a")\n```\nIn this example we use two variables, a and b, which are used as part of the if statement to test whether b is greater than a. As a is 33, and b is 200, we know that 200 is greater than 33, and so we print to screen that "b is greater than a".\n\n**Elif statement**\nThe `elif` keyword is pythons way of saying "if the previous conditions were not true, then try this condition".\n\n```\na = 33\nb = 33\nif b > a:\n  print("b is greater than a")\nelif a == b:\n  print("a and b are equal")\n```\n\n**Else statement**\nThe `else` keyword catches anything which isn\'t caught by the preceding conditions.\n\n```\na = 200\nb = 33\nif b > a:\n  print("b is greater than a")\nelif a == b:\n  print("a and b are equal")\nelse:\n  print("a is greater than b")\n```\n\n**Indentation**\nPython relies on indentation (whitespace at the beginning of a line) to define scope in the code.', colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "loop" in args or "loops" in args:
                embed = discord.Embed(title="Loops", description='Python has two primitive loop commands:\n> `while` loops\n> `for` loops\n\n**While loop**\nWith the `while` loop we can execute a set of statements as long as a condition is true.\nPrint i as long as i is less than 6:\n```\ni = 1\nwhile i < 6:\n  print(i)\n  i += 1\n```\n\n**For loop**\nA for loop is used for iterating over a sequence (that is either a list, a tuple, a dictionary, a set, or a string).\nWith the for loop we can execute a set of statements, once for each item in a list, tuple, set etc.\nPrint each fruit in a fruit list:\n```\nfruits = ["apple", "banana", "cherry"]\nfor x in fruits:\n  print(x)\n```\n\n**Break statement**\nWith the `break` statement we can stop the loop even if the while condition is true.\nExit the loop when i is 3:\n```\ni = 1\nwhile i < 6:\n  print(i)\n  if i == 3:\n    break\n  i += 1\n```\n\n**Continue statement**\nWith the `continue` statement we can stop the current iteration of the loop, and continue with the next:\n```\nfruits = ["apple", "banana", "cherry"]\nfor x in fruits:\n  if x == "banana":\n    continue\n  print(x)\n```', colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "function" in args or "functions" in args:
                embed = discord.Embed(title="Functions", description='A function is a block of code which only runs when it is called.\nYou can pass data, known as parameters, into a function.\nA function can return data as a result.\n\nA function is defined using the `def` keyword:\n```\ndef my_function():\n  print("Hello from a function")\n```\n\nTo call a function, use the function name followed by parenthesis:\n```\nmy_function()\n```\n\n**Arguments**\nInformation can be passed into functions as arguments. Arguments are specified after the function name, inside the parentheses. You can add as many arguments as you want, just separate them with a comma.\n```\ndef my_function(fruit):\n   print("The fruit is " + fruit)\n\nmy_function("apple")\n```\n\n**Number of arguments**\nBy default, a function must be called with the correct number of arguments. Meaning that if your function expects 2 arguments, you have to call the function with 2 arguments, not more, and not less.\nThis function expects 2 arguments, and gets 2 arguments:\n```\ndef my_function(fname, lname):\n  print(fname + " " + lname)\nmy_function("Carl", "Jeffrey")\n```\nIf you try to call the function with 1 or 3 arguments, you will get an error.\n\n**Return values**\nTo let a function return a value, use the return statement:\n```\ndef my_function(x):\n  return 5 * x\nprint(my_function(3))\nprint(my_function(5))\n```', colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "class" in args or "classes" in args or "object" in args or "objects" in args:
                embed = discord.Embed(title="Classes/Objects", description='To create a class, use the keyword `class`:\nCreate a class named MyClass, with a property named x:\n```\nclass MyClass:\n  x = 5\n```\nNow we can use the class named MyClass to create objects:\nCreate an object named p1, and print the value of x:\n```\np1 = MyClass()\nprint(p1.x)\n```\n\n**The \_\_init\_\_() function**\nTo understand the meaning of classes we have to understand the built-in \_\_init\_\_() function.\nAll classes have a function called \_\_init\_\_(), which is always executed when the class is being initiated.\nUse the \_\_init\_\_() function to assign values to object properties, or other operations that are necessary to do when the object is being created:\n```\nclass Person:\n  def __init__(self, name, age):\n    self.name = name\n    self.age = age\np1 = Person("John", 36)\nprint(p1.name)\nprint(p1.age)\n```\n**The self parameter**\nThe `self` parameter is a reference to the current instance of the class, and is used to access variables that belongs to the class.\nIt does not have to be named `self`, you can call it whatever you like, but it has to be the first parameter of any function in the class.\n\n**Modify object properties**\nYou can modify properties on objects like this:\nSet the age of p1 to 40:\n```\np1.age = 40\n```\n**Delete object properties**\nYou can delete properties on objects by using the del keyword:\nDelete the age property from the p1 object:\n```\ndel p1.age\n```', colour=discord.Colour.orange())
                await ctx.send(embed=embed)
            elif "datetime" in args or "date" in args or "date" in args and "time" in args:
                embed = discord.Embed(title="Datetime", description='A date in Python is not a data type of its own, but we can import a module named datetime to work with dates as date objects.\n\nImport the datetime module and display the current date:\n```\nimport datetime\n\nx = datetime.datetime.now()\nprint(x)\n```\nWhen we execute the code from the example above the result will be `2021-03-25 19:24:31.217979`\nThe date contains year, month, day, hour, minute, second, and microsecond.\nReturn the year and name of weekday:\n```\nimport datetime\nx = datetime.datetime.now()\nprint(x.year)\nprint(x.strftime("%A"))\n```\nTo create a date, we can use the datetime() class (constructor) of the datetime module.\n\nThe **datetime()** class requires three parameters to create a date: year, month, day.\n```\nimport datetime\n\nx = datetime.datetime(2021, 5, 17)\n\nprint(x)\n```\nThe datetime() class also takes parameters for time and timezone (hour, minute, second, microsecond, tzone), but they are optional, and has a default value of 0, (None for timezone).', colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "module" in args or "modules" in args:
                embed = discord.Embed(title="Modules", description='Consider a module to be the same as a code library.\nA file containing a set of functions you want to include in your application.\n\nTo create a module just save the code you want in a file with the file extension `.py`:\nSave this code in a file named mymodule.py\n```\ndef greeting(name):\n  print("Hello, " + name)\n```\nNow we can use the module we just created, by using the `import` statement:\nImport the module named mymodule, and call the greeting function:\n```\nimport mymodule\n\nmymodule.greeting("John")\n```\n> When using a function from a module, use the syntax: module_name.function_name\n\n**Variables in modules**\nThe module can contain functions, as already described, but also variables of all types:\nSave this code in the file mymodule.py\n```\nperson1 = {\n  "name": "John",\n  "age": 36,\n  "country": "Norway"\n}\n```\nImport the module named mymodule, and access the person1 dictionary:\n```\nimport mymodule\na = mymodule.person1["age"]\nprint(a)\n```\nYou can name a module whatever you like, but it must have the file extension `.py`\n\n**Import from module**\nYou can choose to import only parts from a module, by using the from keyword.\nImport only the person1 dictionary from the module:\n```\nfrom mymodule import person1\n\nprint(person1["age"])\n```', colour=discord.Colour.orange())
                await ctx.send(embed=embed)
            elif "json" in args:
                embed = discord.Embed(title="JSON", description='JSON is a syntax for storing and exchanging data. It is text, written with JavaScript object notation.\n\nPython has a built-in package called `json`, which can be used to work with JSON data: `import json`\n**Parse JSON - Convert from JSON to Python**\nIf you have a JSON string, you can parse it by using the `json.loads()` method.\n\n```\nimport json\n# some JSON:\nx = \'{ "name":"John", "age":30, "city":"New York"}\'\n# parse x:\ny = json.loads(x)\n# the result is a Python dictionary:\nprint(y["age"])\n```\n**Convert from Python to JSON**\nIf you have a Python object, you can convert it into a JSON string by using the json.dumps() method.\n\n```\nimport json\n# a Python object (dict):\nx = {\n  "name": "John",\n  "age": 30,\n  "city": "New York"\n}\n# convert into JSON:\ny = json.dumps(x)\n# the result is a JSON string:\nprint(y)\n```\n**Read and write to a JSON file**\n```\nimport json\n\nwith open("animals.json") as file:\n   animals = json.load(file) # Read file\nanimals["animals"] = ["dog", "cat"] # Change the list\nprint(animals["animals])\n\nwith open("animals.json", "w") as file:\n   json.dump(animals, file  # Write the new list to the file\n```', colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "arithmetic" in args and "operator" in args or "arithmetic" in args and "operators" in args:
                embed = discord.Embed(title="Arithmetic operators", description="Operator | Name\n\n> **+**   Addition\n> **-**   Subtraction\n> *****   Multiplication\n> **/**   Division\n> **%**   Modulus\n> ******   Exponentiation\n> **//**   Floor division", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "assignment" in args and "operator" in args or "assignment" in args and "operators" in args:
                embed = discord.Embed(title="Assignment operators", description="Operator\n\n> **=**\n> **+=**\n> **-=**\n> *****\n> **/=**\n> **%=**\n> **//**\n> ****=**", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "comparison" in args and "operator" in args or "comparison" in args and "operators" in args:
                embed = discord.Embed(title="Comparison operators", description="Operator | Name\n\n> **==**    Equal\n> **!=**    Not equal\n> **>**    Great than\n> **<**    Less than\n> **>=**   Greater than or equal to\n> **<=**   Less than or equal to", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "logical" in args and "operator" in args or "logical" in args and "operators" in args:
                embed = discord.Embed(title="Logical operators", description="Operator | Description\n\n> **and**     Returns True if both\n>       statements are true\n> **or**     Returns True if one\n>       of the statements is true\n> **not**    Reverse the result, returns\n>       False if the result is true", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "identity" in args and "operator" in args or "identity" in args and "operators" in args:
                embed = discord.Embed(title="Identity operators", description="Operator | Description\n\n> **is**    Returns True if both\n>      variables are the same object\n> **is not**  Returns True if both\n>      variables are not the same object", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            elif "membership" in args and "operator" in args or "membership" in args and "operators" in args:
                embed = discord.Embed(title="Membership operators", description="Operator | Description\n\n> **in**   Returns True if a sequence with\n>  the specified value is present in the object\n> **not in**  Returns True if a sequence with\n>  the specified value is present in the object", colour=discord.Colour.teal())
                await ctx.send(embed=embed)
            else:
                await ctx.send("That category does not exist. Make sure you spelled it right.")

    @commands.command(help="Get information about common python errors.", description="name (Required): Error name", usage="error <name>")
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

    def parse_object_inv(self, stream, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            sub = cache[key] = {}
            async with self.session.get(page + '/objects.inv') as resp:
                if resp.status != 200:
                    raise RuntimeError('Cannot build rtfm lookup table, try again later.')

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    def finder(self, text, collection, *, key=None, lazy=True):
        suggestions = []
        text = str(text)
        pat = '.*?'.join(map(re.escape, text))
        regex = re.compile(pat, flags=re.IGNORECASE)
        for item in collection:
            to_search = key(item) if key else item
            r = regex.search(to_search)
            if r:
                suggestions.append((len(r.group()), r.start(), item))

        def sort_key(tup):
            if key:
                return tup[0], tup[1], key(tup[2])
            return tup

        if lazy:
            return (z for _, _, z in sorted(suggestions, key=sort_key))
        else:
            return [z for _, _, z in sorted(suggestions, key=sort_key)]

    async def do_rtfm(self, ctx, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'python': 'https://docs.python.org/3',
            'master': 'https://discordpy.readthedocs.io/en/master',
        }

        if not hasattr(self, '_rtfm_cache'):
            await ctx.trigger_typing()
            await self.build_rtfm_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            # point the abc.Messageable types properly:
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())

        matches = self.finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        e = discord.Embed(colour=discord.Colour.blurple())
        if len(matches) == 0:
            return await ctx.send(':warning: Could not find anything.')

        e.title = f"{len(matches)} results found for `{obj}`."
        e.description = '\n'.join(f'[`{key}`]({url})' for key, url in matches)
        await ctx.send(embed=e)

    @commands.group(aliases=['docs', 'documentation', 'doc'], invoke_without_command=True, help="Search python (docs syntax) or discord.py (docs dpy Bot) documentation.", description="option (Optional): dpy to search discord.py docs\nkeyword(s) (Required): Search keyword(s)", usage="docs [option] <keyword(s)>")
    async def rtfm(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity.
        Events, objects, and functions are all supported through a
        a cruddy fuzzy algorithm.
        """
        if obj is None:
            await ctx.send("https://docs.python.org/3")
            return
        elif obj == "dpy":
            await ctx.send("https://discordpy.readthedocs.io/en/master")
            return
        if obj.startswith("dpy"):
            obj = obj[4:]
            await self.do_rtfm(ctx, "master", obj)
        else:
            await self.do_rtfm(ctx, 'python', obj)

    async def rtfm_python(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a Python entity."""
        await self.do_rtfm(ctx, 'python', obj)

    async def rtfm_master(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity (master branch)"""
        await self.do_rtfm(ctx, 'master', obj)

def setup(bot):
    bot.add_cog(python(bot))
