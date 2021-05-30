from discord.ext import commands
import discord
import asyncio
import signal
from sandbox import Sandbox

class Evaluation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["e", "evaluation"])
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
                message = await ctx.send(f"{ctx.author.mention} {output}")
            except discord.HTTPException:
                await ctx.send(f":warning: Your eval job has completed with return code 0.\n\n```[Too long message]             ```")
                return

            emoji = self.bot.get_emoji(833349328277471282)
            await message.add_reaction(emoji)

            def check(react, react_user):
                return react_user == ctx.author and react.emoji.id == 833349328277471282

            try:
                await self.bot.wait_for("reaction_add", check=check, timeout=20)
                await message.edit(content=f"{ctx.author.name}'s code evaluation was deleted.", delete_after=5)
            except asyncio.TimeoutError:
                return

    @eval.error
    async def eval_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Add the code you want to execute. Example: `eval print(2 - 2)`")

def setup(bot):
    bot.add_cog(Evaluation(bot))
