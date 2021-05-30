from discord.ext import commands
import discord
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import os
category = None
users = []

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db["profiles"]

message_id = 841405681475125298

class StackOverflow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_new_rank(self, guild, author, amount):
        print(author.id)
        user = collection.find_one({"_id": author.id})
        previous_points = user["points"]
        collection.update_one({"_id": author.id}, {"$set": {"points": user["points"] + amount}})
        rank_channel = self.bot.get_channel(799368863720144896) or await self.bot.fetch_channel(799368863720144896)
        if previous_points <= 500 and user["points"] >= 500:
            await rank_channel.send(f"{author.mention} has earned a new rank!\nThey are now rank **Starter**.")
            collection.update_one({"_id": author.id}, {"$set": {"rank": "starter"}})
            await author.add_roles(guild.get_role(841409362672091196))
        elif previous_points <= 1500 and user["points"] >= 1500:
            await rank_channel.send(f"{author.mention} has earned a new rank!\nThey are now rank **Intermediate**.")
            collection.update_one({"_id": author.id}, {"$set": {"rank": "intermediate"}})
            await author.remove_roles(guild.get_role(841409362672091196))
            await author.add_roles(guild.get_role(841409519053307955))
        elif previous_points <= 3000 and user["points"] >= 3000:
            await rank_channel.send(f"{author.mention} has earned a new rank!\nThey are now rank **Active Helper**.")
            collection.update_one({"_id": author.id}, {"$set": {"rank": "active helper"}})
            await author.remove_roles(guild.get_role(841409519053307955))
            await author.add_roles(guild.get_role(841409620488224768))
        elif previous_points <= 10000 and user["points"] >= 10000:
            await rank_channel.send(f"{author.mention} has earned a new rank!\nThey are now rank **Dev Nerd**.")
            collection.update_one({"_id": author.id}, {"$set": {"rank": "dev nerd"}})
            await author.remove_roles(guild.get_role(841409620488224768))
            await author.add_roles(guild.get_role(841409703929053205))
        elif previous_points <= 50000 and user["points"] >= 50000:
            await rank_channel.send(f"{author.mention} has earned a new rank!\nThey are now rank **Stack Pro**.")
            collection.update_one({"_id": author.id}, {"$set": {"rank": "stack pro"}})
            await author.remove_roles(guild.get_role(841409703929053205))
            await author.add_roles(guild.get_role(841409894116491314))

    @commands.command()
    async def createprofile(self, ctx):
        if ctx.guild.id != 799328665442713600:
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            collection.insert_one({"_id": ctx.author.id, "solutions": 0, "questions": 0, "rank": "None", "points": 0})
            await ctx.send("**Profile created!**\n You can now open questions in <#841398524208873492> and earn points by answering, commenting and getting answers marked as solutions.\nFor more info use `py help questions`")
        else:
            await ctx.send("You already have a profile.")
            return

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        if ctx.guild.id != 799328665442713600:
            return
        if member is None:
            user = collection.find_one({"_id": ctx.author.id})
            if user is None:
                await ctx.send("You don't have a profile. Create it with `createprofile`")
                return
            em = discord.Embed(title=f"{ctx.author.name}'s profile",
                               description=f"Solutions: **{user['solutions']} ** :bulb:ㅤㅤㅤㅤㅤㅤ\nQuestions asked: **{user['questions']}** :pushpin: \n\nRank: {user['rank']}\nPoints: {user['points']} :comet:",
                               colour=discord.Colour.orange())
            em.set_thumbnail(url=ctx.author.avatar_url)
        else:
            user = collection.find_one({"_id": member.id})
            if user is None:
                await ctx.send("That member doesn't have a profile.")
            em = discord.Embed(title=f"{member.name}'s profile",
                               description=f"Solutions: **{user['solutions']}**ㅤㅤㅤㅤㅤㅤ\nQuestions asked: **{user['questions']}**\n\nRank: {user['rank']}\nPoints: {user['points']} :comet:",
                               colour=discord.Colour.orange())
            em.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=em)

    @commands.command()
    async def comment(self, ctx,  *, text: str):
        if ctx.guild.id != 799328665442713600:
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.author.send("You must have a profile to use this command, create it with `createprofile` in <#799368863720144896>")
            return
        messages = await ctx.channel.history(limit=1, oldest_first=True).flatten()
        message = messages[0]
        question_embed = messages[0].embeds[0]
        global category
        if category is None:
            category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(841398204280078357)
        if message.channel not in category.channels:
            await ctx.send("You are not in the appropriate channel.")
            return
        await self.check_new_rank(ctx.guild, ctx.author, 25)
        embed = discord.Embed(title=f"Comment", description=text, colour=int("0x36393f", 16), timestamp=datetime.now())
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        msg = await message.channel.send(embed=embed)

        em = discord.Embed(title=f"Comment On Your Question", description=text + f"\n\nGo to comment: **[CLICK]({msg.jump_url})**", colour=discord.Colour.orange(), timestamp=datetime.now())
        em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        author_id = question_embed.footer.text.split("User ID: ")[1]
        author = self.bot.get_user(int(author_id)) or await self.bot.fetch_user(int(author_id))
        await author.send(embed=em)

    @commands.command()
    async def answer(self, ctx, *, text: str):
        if ctx.guild.id != 799328665442713600:
            return
        user = collection.find_one({"_id": ctx.author.id})
        if user is None:
            await ctx.author.send("You must have a profile to use this command, create it with `createprofile` in <#799368863720144896>")
            return
        messages = await ctx.channel.history(limit=1, oldest_first=True).flatten()
        message = messages[0]
        question_embed = messages[0].embeds[0]
        global category
        if category is None:
            category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(841398204280078357)
        if message.channel not in category.channels:
            await ctx.send("You are not in the appropriate channel.")
            return
        elif f"{ctx.author.name}#{ctx.author.discriminator}" == question_embed.author.name:
            await ctx.send("You cannot answer yourself.")
            return
        await self.check_new_rank(ctx.guild, ctx.author, 45)
        embed = discord.Embed(title=f"Answer", description=text, colour=int("0x36393f", 16), timestamp=datetime.now())
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        msg = await message.channel.send(embed=embed)
        embed.set_footer(text=f"Answer ID: {msg.id} | User ID: {ctx.author.id}")
        await msg.edit(embed=embed)

        em = discord.Embed(title=f"Answer On Your Question {message.embeds[0].title}", description=text + f"\n\nGo to answer: **[CLICK]({msg.jump_url})**", colour=discord.Colour.orange(), timestamp=datetime.now())
        em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        author_id = question_embed.footer.text.split("User ID: ")[1]
        author = self.bot.get_user(int(author_id)) or await self.bot.fetch_user(int(author_id))
        await author.send(embed=em)

    @commands.command()
    async def close(self, ctx):
        if ctx.guild.id != 799328665442713600:
            return
        await ctx.message.add_reaction("✅")
        user = ctx.author
        global category
        if category is None:
            category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(841398204280078357)
        if ctx.channel not in category.channels:
            await ctx.send("You are not in the appropriate channel.")
            return
        messages = await ctx.channel.history(limit=1, oldest_first=True).flatten()
        message = messages[0]
        await ctx.author.send("Are you sure you want to delete this question? Enter `yes` or `no`.", embed=message.embeds[0])

        def check2(msg):
            return msg.author.id == user.id and msg.channel == user.dm_channel and msg.content.lower() in ["post", "cancel"]
        try:
            msg2 = await self.bot.wait_for('message', check=check2, timeout=180)
            if msg2.content == "yes":
                await ctx.channel.delete(reason=f"Question by {ctx.author.name}#{ctx.author.discriminator} closed")
                await ctx.author.send("Question successfully deleted.")
            elif msg2.content == "no":
                await ctx.author.send("Canceled.")
        except asyncio.TimeoutError:
            await user.send("Prompt canceled due to no response.")

    @commands.command()
    async def solution(self, ctx, msg_id: int, name=None, discriminator=None, avatar_url=None):
        if ctx.guild.id != 799328665442713600:
            return
        global category
        if category is None:
            category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(841398204280078357)
        if ctx.channel not in category.channels:
            await ctx.send("You are not in the appropriate channel.")
            return
        messages = await ctx.channel.history(limit=1, oldest_first=True).flatten()
        question_embed = messages[0].embeds[0]
        if name is None and discriminator is None and avatar_url is None:
            name = ctx.author.name
            discriminator = ctx.author.discriminator
            avatar_url = ctx.author.avatar_url
        if question_embed.author.name == f"{name}#{discriminator}":
            try:
                message = await ctx.channel.fetch_message(msg_id)
                await message.add_reaction("✅")
            except discord.NotFound:
                await ctx.send("A message with that id could not be found.", delete_after=3)
                return
            if message.channel not in category.channels:
                await ctx.send("That answer ID is not valid, make sure you are in the right", delete_after=3)
                return
            elif message.embeds[0].title == "Comment":
                await ctx.send("You cannot mark a comment as an answer.", delete_after=3)
                return
            elif message.author == question_embed.author:
                await ctx.send("You cannot mark your message as the answer.", delete_after=3)
                return
            author_id = message.embeds[0].footer.text.split("User ID: ")[1]
            author = self.bot.get_user(int(author_id)) or await self.bot.fetch_user(int(author_id))
            em = discord.Embed(title=f"Answer by {author.name}#{author.discriminator} has been marked as the solution.", description="The channel will be closed in 1 minute. The question and the solution will be in <#839792890455523348>", color=discord.Colour.green())
            em.set_author(name="", icon_url=message.author.avatar_url)
            await ctx.send(embed=em)
            await asyncio.sleep(60)
            await ctx.channel.delete()
            previous_questions = self.bot.get_channel(841398408988065852) or await self.bot.fetch_channel(841398408988065852)
            embed = discord.Embed(title=f"Question {question_embed.title}", description=f"{question_embed.description}\n\n**Solution by {author.name}#{author.discriminator}:**\n{message.embeds[0].description}", timestamp=datetime.now(), colour=discord.Colour.dark_green())
            embed.set_author(name=f"{question_embed.author.name}", icon_url=avatar_url)
            embed.set_footer(text=f"Question ID: {messages[0].id}")
            msg2 = await previous_questions.send(embed=embed)

            await self.check_new_rank(ctx.guild, ctx.author, 20)
            await self.check_new_rank(ctx.guild, author, 200)
            user2 = collection.find_one({"_id": author.id})
            collection.update_one({"_id": author.id}, {"$set": {"solutions": user2["solutions"] + 1}})
            em = discord.Embed(title=f"Your answer was marked as the solution",
                               description=f"**Question**: {msg2.embeds[0].title[9:]}\n{msg2.embeds[0].description.split('Solution by')[0]}\n**Your answer**:{msg2.embeds[0].description.split(f'{author.name}#{author.discriminator}:')[1]}" + f"\nYou earned **200 :comet: points.**\n\nGo to answer: **[CLICK]({msg2.jump_url})**",
                               colour=discord.Colour.orange(), timestamp=datetime.now())
            em.set_author(name=f"{name}#{discriminator}", icon_url=avatar_url)
            await author.send(embed=em)

    @commands.command()
    async def question(self, ctx=None, payload=None):
        try:
            if ctx.guild.id != 799328665442713600:
                return
        except AttributeError:
            pass
        global category
        if type(payload) == discord.RawReactionActionEvent:
            user_db = collection.find_one({"_id": payload.member.id})
            if user_db is None:
                await payload.member.send(
                    "You must have a profile to use this command, create it with `createprofile` in <#799368863720144896>")
                return
            user = payload.member
            react_channel = self.bot.get_channel(841398524208873492) or await self.bot.fetch_channel(841398524208873492)
            react_message = await react_channel.fetch_message(841405681475125298)
            await react_message.remove_reaction("❓", user)

            embed = discord.Embed(title="Question Prompt",
                                  description="What is your question? It needs to be between 15 and 100 characters long.\nSend `cancel` to end the prompt.",
                                  colour=discord.Colour.orange())
            embed.set_footer(text="The prompt will end in 3 minutes.")
            await user.send(embed=embed)

            def check(message):
                return message.author == user and message.channel == user.dm_channel

            end = time.time() + 180
            seconds = 180
            while True:
                msg = await self.bot.wait_for("message", check=check, timeout=seconds)
                if msg.content.lower() == "cancel":
                    await user.send("Prompt canceled.")
                    return
                elif len(msg.content) < 15:
                    seconds = end - time.time()
                    embed = discord.Embed(title="Prompt Invalid Input",
                                          description="Minimum of 15 characters is required.\n Please retry or `cancel` to end the prompt.",
                                          colour=discord.Colour.red())
                    m = round((seconds // 60) % 60)
                    s = round(seconds % 60)
                    embed.set_footer(text=f"The prompt will end in {m} minutes and {s} seconds.")
                    await user.send(embed=embed)
                elif len(msg.content) > 100:
                    seconds = end - time.time()
                    embed = discord.Embed(title="Prompt Invalid Input",
                                          description="Maximum of 100 characters is required.\n Please retry or `cancel` to end the prompt.",
                                          colour=discord.Colour.red())
                    m = round((seconds // 60) % 60)
                    s = round(seconds % 60)
                    embed.set_footer(text=f"The prompt will end in {m} minutes and {s} seconds.")
                    await user.send(embed=embed)
                else:
                    question = msg.content
                    break
            embed = discord.Embed(title="Description Prompt",
                                  description="Enter a detailed description of your question. It needs to be at least 100 characters long.\nInclude as much information as you can, your code, errors, things you tried.\nMake sure to use the discord formatting when pasting any code:\n\```\n# code here\n\```\nSend cancel to end the prompt.",
                                  colour=discord.Colour.orange())
            embed.set_footer(text="The prompt will end in 10 minutes.")
            await user.send(embed=embed)

            end = time.time() + 600
            seconds = 600
            while True:
                msg = await self.bot.wait_for("message", check=check, timeout=seconds)
                if msg.content.lower() == "cancel":
                    await user.send("Prompt canceled.")
                    return
                elif len(msg.content) < 100:
                    seconds = end - time.time()
                    embed = discord.Embed(title="Prompt Invalid Input",
                                          description=f"Minimum of 100 characters is required, your description is {len(msg.content)} characters long.\n Please retry or `cancel` to end the prompt.",
                                          colour=discord.Colour.red())
                    m = round((seconds // 60) % 60)
                    s = round(seconds % 60)
                    embed.set_footer(text=f"The prompt will end in {m} minutes and {s} seconds.")
                    await user.send(embed=embed)
                else:
                    description = msg.content
                    break
            post_embed = discord.Embed(title=question.capitalize(), description=description, colour=discord.Colour.green())
            post_embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar_url)
            post_embed.set_footer(text="The prompt will end in 3 minutes.")

            await user.send("Preview of your question. Enter `post` to post or `cancel` to cancel.", embed=post_embed)

            def check2(msg):
                return msg.author.id == user.id and msg.channel == user.dm_channel and msg.content.lower() in ["post",
                                                                                                               "cancel"]
            try:
                message = await self.bot.wait_for('message', timeout=180, check=check2)
                if message.content == "post":
                    posting_message = await user.send("<a:loading_pic:833966183841529916> Posting your question...")

                    if category is None:
                        category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(
                            841398204280078357)
                    question_channel = await category.create_text_channel(name=question[:-1])
                    message = await question_channel.send(embed=post_embed)
                    await message.pin()
                    post_embed.set_footer(text=f"User ID: {payload.user_id}")
                    await message.edit(embed=post_embed)

                    await posting_message.delete()
                    embed = discord.Embed(title="Question posted!",
                                          description=f"Go to the message: **[CLICK]({message.jump_url})**\nID: {message.id}\n\nTo mark someones answer as the solution react to the answer with :white_check_mark: \nor send `py solution <message id>`\nIt will also archive the question and its solution.\nYou can also delete the question with `py delete` in that question channel.",
                                          colour=discord.Colour.green())
                    await user.send(embed=embed)
                    collection.update_one({"_id": user.id}, {"$set": {"questions": user_db["questions"] + 1}})
                    await self.check_new_rank(
                        self.bot.get_guild(payload.guild_id) or await self.bot.fetch_guild(payload.guild_id),
                        user,
                        10)
                elif message.content == "cancel":
                    await user.send("Prompt canceled.")
            except asyncio.TimeoutError:
                await user.send("Prompt canceled due to no response.")
        else:
            user_db = collection.find_one({"_id": ctx.author.id})
            if user_db is None:
                await ctx.author.send(
                    "You must have a profile to use this command, create it with `createprofile` in <#799368863720144896>")
                return
            await ctx.message.add_reaction("✅")
            user = ctx.author
            react_channel = self.bot.get_channel(841398524208873492) or await self.bot.fetch_channel(841398524208873492)
            react_message = await react_channel.fetch_message(841405681475125298)
            await react_message.remove_reaction("❓", ctx.author)

            embed = discord.Embed(title="Question Prompt",
                                  description="What is your question? It needs to be between 15 and 100 characters long.\nSend `cancel` to end the prompt.",
                                  colour=discord.Colour.orange())
            embed.set_footer(text="The prompt will end in 3 minutes.")
            await user.send(embed=embed)

            def check(message):
                return message.author == user and message.channel == user.dm_channel

            end = time.time() + 180
            seconds = 180
            while True:
                try:
                    msg = await self.bot.wait_for("message", check=check, timeout=seconds)
                    if msg.content.lower() == "cancel":
                        await user.send("Prompt canceled.")
                        return
                    elif len(msg.content) < 15:
                        seconds = end - time.time()
                        embed = discord.Embed(title="Prompt Invalid Input",
                                              description="Minimum of 15 characters is required.\n Please retry or `cancel` to end the prompt.",
                                              colour=discord.Colour.red())
                        m = round((seconds // 60) % 60)
                        s = round(seconds % 60)
                        embed.set_footer(text=f"The prompt will end in {m} minutes and {s} seconds.")
                        await user.send(embed=embed)
                    elif len(msg.content) > 100:
                        seconds = end - time.time()
                        embed = discord.Embed(title="Prompt Invalid Input",
                                              description="Maximum of 100 characters is required.\n Please retry or `cancel` to end the prompt.",
                                              colour=discord.Colour.red())
                        m = round((seconds // 60) % 60)
                        s = round(seconds % 60)
                        embed.set_footer(text=f"The prompt will end in {m} minutes and {s} seconds.")
                        await user.send(embed=embed)
                    else:
                        question = msg.content
                        break
                except asyncio.TimeoutError:
                    await ctx.send("Prompt canceled due to no response.")
                    return
            embed = discord.Embed(title="Description Prompt",
                                  description="Enter a detailed description of your question. It needs to be at least 100 characters long.\nInclude as much information as you can, your code, errors, things you tried.\nMake sure to use the discord formatting when pasting any code:\n\```\n# code here\n\```\nSend cancel to end the prompt.",
                                  colour=discord.Colour.orange())
            embed.set_footer(text="The prompt will end in 10 minutes.")
            await user.send(embed=embed)

            end = time.time() + 600
            seconds = 600
            while True:
                msg = await self.bot.wait_for("message", check=check, timeout=seconds)
                if msg.content.lower() == "cancel":
                    await user.send("Prompt canceled.")
                    return
                elif len(msg.content) < 100:
                    seconds = end - time.time()
                    embed = discord.Embed(title="Prompt Invalid Input",
                                          description=f"Minimum of 100 characters is required, your description is {len(msg.content)} characters long.\n Please retry or `cancel` to end the prompt.",
                                          colour=discord.Colour.red())
                    m = round((seconds // 60) % 60)
                    s = round(seconds % 60)
                    embed.set_footer(text=f"The prompt will end in {m} minutes and {s} seconds.")
                    await user.send(embed=embed)
                else:
                    description = msg.content
                    break
            post_embed = discord.Embed(title=question.capitalize(), description=description, colour=discord.Colour.green())
            post_embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar_url)
            post_embed.set_footer(text="The prompt will end in 3 minutes.")

            await user.send("Preview of your question. Enter `post` to post or `cancel` to cancel.", embed=post_embed)

            def check2(msg):
                return msg.author.id == user.id and msg.channel == user.dm_channel and msg.content.lower() in ["post",
                                                                                                               "cancel"]
            try:
                message = await self.bot.wait_for('message', timeout=180, check=check2)
                if message.content == "post":
                    posting_message = await user.send("<a:loading_pic:833966183841529916> Posting your question...")

                    if category is None:
                        category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(
                            841398204280078357)
                    question_channel = await category.create_text_channel(name=question)
                    message = await question_channel.send(embed=post_embed)
                    await message.pin()
                    post_embed.set_footer(text=f"User ID: {message.author.id}")
                    await message.edit(embed=post_embed)

                    await posting_message.delete()
                    embed = discord.Embed(title="Question posted!",
                                          description=f"Go to the message: **[CLICK]({message.jump_url})**\nID: {message.id}\n\nTo mark someones answer as the solution react to the answer with :white_check_mark: \nor send `py solution <message id>`\nIt will also archive the question and its solution.\nYou can also delete the question with `py delete` in that question channel.",
                                          colour=discord.Colour.green())
                    await user.send(embed=embed)
                    user2 = collection.find_one({"_id": ctx.author.id})
                    collection.update_one({"_id": ctx.author.id}, {"$set": {"questions": user2["questions"] + 1}})
                    await self.check_new_rank(
                        await self.bot.get_guild(ctx.guild.id) or await self.bot.fetch_guild(ctx.guild.id),
                        user,
                        10)
                elif message.content == "cancel":
                    await user.send("Prompt canceled.")
            except asyncio.TimeoutError:
                await user.send("Prompt canceled due to no response.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id != 799328665442713600:
            return
        if payload.event_type == "REACTION_REMOVE":
            return
        if str(payload.emoji) == "❓" and payload.message_id == message_id and not payload.member.bot:
            await self.question(None, payload)
        elif str(payload.emoji) == "✅" and not payload.member.bot:
            lst = []
            global category
            if category is None:
                category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(841398204280078357)
            for channel in category.channels:
                lst.append(channel.id)
            if payload.channel_id not in lst:
                return

            channel = self.bot.get_channel(payload.channel_id) or await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            return await self.solution(await self.bot.get_context(message), payload.message_id, payload.member.name, payload.member.discriminator, payload.member.avatar_url)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.guild.id != 799328665442713600:
            return
        if message.author.bot or message.guild.id != 799328665442713600:
            return
        global category
        if category is None:
            category = self.bot.get_channel(841398204280078357) or await self.bot.fetch_channel(841398204280078357)
        if message.channel in category.channels:
            messages = await message.channel.history(limit=1, oldest_first=True).flatten()
            question_embed = messages[0].embeds[0]
            try:
                author_id = question_embed.footer.text.split("User ID: ")[1]
            except AttributeError:
                return
            if message.author.id == int(author_id):
                return
            if message.author.id != question_embed.author.id and not message.content.lower().startswith('py') or message.author != question_embed.author and not message.content.lower().startswith('py') or message.author != question_embed.author and not message.content.lower().startswith('py'):
                await message.author.send("Only the question author can send messages. Others must use the command `answer` (with the prefix).")
                await message.delete()
            elif message.author.id != question_embed.author.id:
                await message.delete()

    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid member type given, you must mention a member or his id.")
            return
        raise error

    @answer.error
    async def answer_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send("What is your answer?\nCorrect usage: `answer <text>`")
            return
        raise error

    @comment.error
    async def comment_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            await ctx.author.send("What is your comment?\nCorrect usage: `comment <text>`")
            return
        raise error

    @solution.error
    async def solution_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            await ctx.author.send("Missing the message id argument.\nCorrect usage: `solution <message id>`")
            return
        raise error

def setup(bot):
    bot.add_cog(StackOverflow(bot))
