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


class CustomHelpCommand(commands.MinimalHelpCommand):
    '''
    Custom Help command.
    This is subclass of commands.MinimalHelpCommand.
    '''

    def __init__(self):
        super().__init__()

    def parse_cogname(self, cog):
        names = {
            'python': ':snake: Python',
            'economy': ':money_with_wings: Economy',
            'config': ':gear: Config',
            'coding': ':keyboard: Code channel',
            'other': ':newspaper: Other'
        }
        return names[cog.qualified_name]

    async def send_cog_help(self, cog):
        channel = self.get_destination()
        cmds = cog.get_commands()

        embed = discord.Embed(title=self.parse_cogname(cog), description=cog.description, color=4879080)
        embed.add_field(name="Commands", value=', '.join(['`' + command.name + '`' for command in cmds]))
        embed.add_field(name="More info", value="For more information on a command, use `help <command>` command.",
                        inline=False)
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        '''
        Sends the help message for a commands.Group object. (Or a command group).
        This embed basically leads the user to use the main group command for more information.
        '''
        channel = self.get_destination()
        embed = discord.Embed(
            title=group.name,
            description=group.help,
            color=4879080
        )

        embed.add_field(name="Commands", value='\n'.join(
            ['`' + group.name + ' ' + command.name + '`' for command in group.commands]
        ))
        embed.add_field(name="More Help",
                        value=f"For information about a command use: `py help {group.name} <command>`",
                        inline=False)
        await channel.send(embed=embed)

    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        embed = discord.Embed(
            title=":question: Help Page",
            description="List of all the categories. Use command for the respective category to get list of commands of that specific category.",
            color=4879080
        )

        if isinstance(self.context.bot.prefix_cache[self.context.guild.id], list):
            prefix = self.context.bot.prefix_cache[self.context.guild.id][0]
        else:
            prefix = self.context.bot.prefixes_cache[self.context.guild.id]
        for key in mapping:
            if key is None:
                pass
            elif key.qualified_name in ['Admin', 'Help', 'StackOverflow', 'TopGG', 'Webserver']:
                pass
            else:
                embed.add_field(
                    name=self.parse_cogname(key),
                    value='`{}help {}`'.format(prefix, key.qualified_name),
                    inline=True)
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        '''
        Sends the help message about a certain command.
        [i] command.help.split(||)[1] is the required permissions if applicable.
        [i] command.description is the arguments help.
        [i] command.usage is the command's usage.
        '''

        channel = self.get_destination()
        embed = discord.Embed(
            title='`' + command.usage + '`',
            description=command.help if '||' not in command.help else command.help.split('||')[0],
            color=4879080
        )

        embed.add_field(name="Arguments",
                        value=command.description, inline=False)

        embed.add_field(name="Required Permissions",
                        value='No special permissions required.' if '||' not in command.help else
                        command.help.split('||')[1], inline=False)

        embed.add_field(name="Aliases ({})".format(len(command.aliases)),
                        value=', '.join(command.aliases) if len(command.aliases) else 'No aliases', inline=False)

        embed.set_footer(
            text='Arguments in <> are required and arguments in [] are optional. Don\'t literally type <> or [].')
        await channel.send(embed=embed)

class Help(commands.Cog):
    '''
    This cog has the help command for bot.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = CustomHelpCommand()

# f"Start a career with `py startcareer`.\n\nEarn money by working and leveling up.\nAt levels `3`, `7`, `15` and `25` you will get a better job.\nYour working payout depends on your job. You need to have a laptop to work. Laptops have a small chance to break, a wifi router will reduce the work cooldown.\n\nWhen you reach level 7, you can start a company that can grow big and earn you even more money than a normal job.\n\nVote for the bot on **[top.gg](https://top.gg/bot/800832309989081118/vote)** to get a reward of **$1000**\n\n**Commands:**\n`daily` - claim a reward of $800 every 24 hours\n`career` - see your balance, job and level\n`work` - earn money\n`shop` - buy better equipment\n`buy` - from the shop\n`sell` - your items\n`hack` - steal other users money\n`use` - use an item you bought\n`give` - send money to other members\n`inventory` - see what items you own\n`startcareer`\n`retire` - delete your career data\n`startcompany`\n`shutdowncompany`\n`company`\n\nUsers playing: {users.find({}).count()}"

def setup(bot):
    bot.add_cog(Help(bot))
