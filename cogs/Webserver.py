from aiohttp import web
from discord.ext import commands, tasks
import discord
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from oauth import Oauth
import datetime
import ast
import json
import numpy as np

received_message = {}

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster['python-bot']
collection = db['users']

app = web.Application()
routes = web.RouteTableDef()

def setup(bot):
    bot.add_cog(Webserver(bot))

class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()

        @routes.get('/')
        async def welcome(request):
            return web.Response(text="Hello world!")

        @routes.get('/api')
        async def api(request):
            with open('./api/site.html') as site:
                return web.Response(
                    text=site.read(),
                    content_type='text/html', status=200)

        @routes.post('/api/messages')
        async def message_post(request):
            content_coroutine = await request.text()
            json_content = ast.literal_eval(content_coroutine)
            content = json_content.get("content")
            message_id = np.random.randint(2147483647, 9223372036854775807, size=1, dtype=np.int64)[0]
            if content is None:
                return web.Response(text="fail", status=400)
            global received_message
            received_message = {
                "content": content,
                "id": str(message_id)
            }
            return web.Response(text=json.dumps(received_message), status=200)

        @routes.get('/api/messages')
        async def message_get(request):
            return web.Response(text=json.dumps(received_message), status=200)

        @routes.get("/login")
        async def login(request):
            return web.HTTPFound(Oauth.discord_login_url)

        @routes.get("/redirect")
        async def redirect(request):
            code = request.rel_url.query.get("code")
            if code:
                access_token = Oauth.get_access_token(code)
                user_json = Oauth.get_user_json(access_token)
                user_id = user_json.get("id")
            else:
                user_id = request.rel_url.query.get("userId")
            user = collection.find_one({"_id": int(user_id)})
            if user is None:
                url = f"https://python-bot.web.app/daily?claimed=false"
                return web.HTTPFound(url)
            try:
                last_daily = datetime.datetime.strptime(user["last_daily"], "%Y-%m-%d %H:%M:%S")
                if last_daily <= datetime.datetime.now():
                    date = datetime.datetime.now().replace(microsecond=0)
                    date += datetime.timedelta(days=1)
                    collection.update_one({"_id": int(user_id)}, {"$set": {"last_daily": str(date)}})
                    collection.update_one({"_id": int(user_id)}, {"$set": {"money": user["money"] + 800}})
                    member = await self.bot.fetch_user(int(user_id))
                    await member.send("Daily reward claimed! **$800** for placed in your account.")
                    url = f"https://python-bot.web.app/daily?claimed=true&userId={user_id}"
                else:
                    duration = last_daily - datetime.datetime.now()
                    seconds = duration.total_seconds()
                    hours = round((seconds // 60) // 60)
                    minutes = round((seconds // 60) % 60)
                    seconds = round(seconds % 60)
                    url = f"https://python-bot.web.app/daily?claimed=false&hours={hours}&minutes={minutes}&seconds={seconds}"
            except KeyError:
                date = datetime.datetime.now().replace(microsecond=0)
                date += datetime.timedelta(days=1)
                collection.update_one({"_id": int(user_id)}, {"$set": {"last_daily": str(date)}})
                collection.update_one({"_id": int(user_id)}, {"$set": {"money": user["money"] + 800}})
                url = f"https://python-bot.web.app/daily?claimed=true&userId={user_id}"
                member = await self.bot.fetch_user(int(user_id))
                await member.send("Daily reward claimed! **$800** for placed in your account.")

            return web.HTTPFound(url)

        @routes.post('/dbl')
        async def dblwebhook(request):
            if request.headers.get('authorization') == '3mErTJMYFt':
                data = await request.json()
                user = self.bot.get_user(data['user']) or await self.bot.fetch_user(data['user'])
                if user is None:
                    return
                _type = f'Tested!' if data['type'] == 'test' else f'Voted!'
                upvoted_bot = f'<@{data["bot"]}>'
                embed = discord.Embed(title=_type, colour=discord.Color.blurple())
                embed.description = f'**Upvoter :** {user.mention} Just {_type}' + f'\n**Upvoted Bot :** {upvoted_bot}'
                embed.set_thumbnail(url=user.avatar_url)
                channel = self.bot.get_channel(799698764935331852)
                await channel.send(embed=embed)
                member = collection.find_one({"_id": user.id})
                if member is None:
                    await user.send("Thanks for voting! You can join the support server if you find any bugs or have questions: https://discord.gg/wEWsdEKeEw")
                else:
                    await user.send("Thanks for voting! **Here you go, $1000**. You can join the support server if you find any bugs or have questions: https://discord.gg/wEWsdEKeEw")
                    collection.update_one({"_id": user.id}, {"$set": {"money": member["money"] + 1000}})
                return web.Response(text='success', status=200)
            else:
                return web.Response(text='Unauthorized', status=400)

        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=2000)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()
