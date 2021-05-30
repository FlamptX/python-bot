from discord.ext import commands
from discord_components import Button, ButtonStyle
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
                emoji = self.bot.get_emoji(833349328277471282)
                message = await ctx.send(
                    f"{ctx.author.mention} {output}",
                    components=[
                        Button(style=ButtonStyle.gray, label=" ", emoji=emoji),
                    ]
                )
            except discord.HTTPException:
                message = await ctx.send(
                    f":warning: Your eval job has completed with return code 0.\n\n```[Too long message]             ```",
                    components=[
                        Button(style=ButtonStyle.gray, label=" ", emoji=emoji),
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
            await ctx.send(f"{ctx.author.mention} prompt canceled.")

    @eval.error
    async def eval_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Add the code you want to execute. Example: `eval print(2 - 2)`")

def setup(bot):
    bot.add_cog(Evaluation(bot))
