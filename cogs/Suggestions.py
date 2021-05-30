from discord.ext import commands

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
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
    bot.add_cog(Suggestions(bot))
