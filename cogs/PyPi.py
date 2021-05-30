import discord
from discord.ext import commands
from discord.utils import escape_markdown
import aiohttp
import difflib
try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib

client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
# get a list of package names
packages = client.list_packages()

class PyPi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=("package", "pack"))
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

def setup(bot):
    bot.add_cog(PyPi(bot))
