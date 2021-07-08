from discord.ext import commands
import discord
from datetime import datetime
from discord_components import Button, ButtonStyle

class other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Show the bot and database latency.", description="This command takes no arguments.", usage="ping")
    async def ping(self, ctx):
        start = datetime.now()
        test_guild = self.bot.guild_db.find_one({"_id": 799328665442713600})
        end = datetime.now()
        seconds = (end - start).total_seconds()
        milliseconds = round(seconds * 1000)

        await ctx.send(f"Pong!\n**Bot latency:** {round(self.bot.latency * 1000)}ms\n**Database latency:** {milliseconds}ms")

    @commands.command(help="Information about the bot.", description="This command takes no arguments.", usage="about")
    async def about(self, ctx):
        embed = discord.Embed(colour=discord.Colour.blue(), description=
        f"🐍   Python-Version • 3.8.6\n :page_facing_up:   Discord.py-Version • {discord.__version__}\n ** **\n 📡 Ping • {round(bot.latency * 1000)}ms\n 👾 Hostwebsite • SomethingHost \n :electric_plug: Database • MongoDB \n ** ** \n :chart_with_upwards_trend:  Servers • {len(bot.guilds)} \n :keyboard:  Commands • {len(bot.commands)}\n\nWebsite: https://python-bot.web.app")
        await ctx.send(embed=embed)

    @commands.command(help="Invite the bot to your own server.", description="This command takes no arguments.", usage="invite")
    async def invite(self, ctx):
        embed_var = discord.Embed(title="Invite",
                                  description="Add me to other servers with this link: [**INVITE**](https://discord.com/api/oauth2/authorize?client_id=800832309989081118&permissions=388160&redirect_uri=https%3A%2F%2Fpython-bot.web.app&scope=bot) \n\nWebsite: https://python-bot.web.app\n\n Join the support server: https://discord.gg/wEWsdEKeEw",
                                  color=3447003)
        await ctx.send(
            embed=embed_var,
            components=[
                [
                    Button(style=ButtonStyle.URL, label="Invite",
                           url="https://discord.com/api/oauth2/authorize?client_id=800832309989081118&permissions=388160&redirect_uri=https%3A%2F%2Fpython-bot.web.app&scope=bot"),
                    Button(style=ButtonStyle.URL, label="Support Server", url="https://discord.gg/wEWsdEKeEw"),
                ]
            ]
        )

    @commands.command(help="Vote for the bot on top.gg", description="This command takes no arguments.", usage="vote")
    async def vote(self, ctx):
        embed_var = discord.Embed(title="Upvote",
                                  description="You can support me by **upvoting on top.gg** \n [**VOTE HERE**](https://top.gg/bot/800832309989081118/vote)",
                                  color=discord.Color.blue())
        await ctx.send(
            embed=embed_var,
            components=[
                [
                    Button(style=ButtonStyle.URL, label="Upvote", url="https://top.gg/bot/800832309989081118/vote"),
                ]
            ]
        )

    @commands.command(help="Suggest a new feature or submit an issue.", description="suggestion (Required): The message", usage="suggest <suggestion>")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        if ctx.author.id == 550364713779724288:
            await ctx.send("You are not allowed to use this command.")
            return
        flampt = await self.bot.fetch_user(621309926631014410)
        await flampt.send(f"New suggestion from {ctx.author.name}#{ctx.author.discriminator} in a server \"{ctx.guild.name}\"\n**{suggestion}**\nUser ID: {ctx.author.id}")
        await ctx.send("Suggestion was sent! Your feedback is appreciated.")

    @suggest.error
    async def suggest_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Make a bot suggestion with `suggest {suggestion}`")
            self.suggest.reset_cooldown(ctx)
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Please wait {int(error.retry_after)} seconds before making a new suggestion.")
            return


def setup(bot):
    bot.add_cog(other(bot))
