#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Rahul Zalkikar

import os
import discord
import requests
import time
import aiohttp
import asyncio
import configparser
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TEST_BOT')
GET_REMINDERS = os.getenv('API_ENDPOINT_REMINDERS_BY_SERVER')
API_KEY = os.getenv('API_KEY')
API_URL = 'http://localhost:5050/api/v1/'
CONFIG_PATH = 'conf.ini'

# TODO
# Explain what is happening here.
# Is there a better way to do this?
# Possible Hints:
# How often are bot attributes updated? Is it necessary?
# What is self.loops doing in the reminders task loop?
# Are API Responses always valid? Can we remove any code duplicates?
# How often is the API pinged for data? Is there a better approach?
# What is the difference between using requests vs aiohttp here?

class BotAPI:

    def __init__(self, API, url, session):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        self.session = session
        self.url = config.get(API, url).strip("'")
        self.headers = {
            'Authorization': f'{API_KEY}',
            'Content-Type': 'application/json'
        }

    async def get(self, server_id):
        async with self.session.get(
            API_URL+self.url.format(server_id = server_id),
            headers=self.headers
        ) as res:
            json = await res.json()
            return json

    async def post(self, data):
        async with self.session.post(
            API_URL+self.url,
            json=data,
            headers=self.headers
        ) as res:
            json = await res.json()
            return json

    async def put(self, data):
        async with self.session.put(
            API_URL+self.url,
            json=data,
            headers=self.headers
        ) as res:
            return res.status

    async def delete(self, data):
        async with self.session.delete(
            API_URL+self.url,
            json=data,
            headers=self.headers
        ) as res:
            return res.status

class Manager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.server_ids = []
        self.user_reminders = {}
        self.loops = []
        conn = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
        self.session = aiohttp.ClientSession(connector=conn)

    def add_server(self, server_id: str):
        self.server_ids.append(server_id)
        self.user_reminders[server_id] = []

    async def get_reminders(self, server_id):
        # TODO
        # send a GET request to API Reminders endpoint
        # make sure server_id is request parameter and API key is authorization header
        # hint: ideally use the BotAPI class above (and thereby aiohttp session)
        # ......

    async def send_msg(self, channel, msg, msg_type):
        try:
            sent_msg = None
            if msg_type == 1: # embed
                sent_msg = await channel.send(embed=msg)
            else:
                sent_msg = await channel.send(msg)
            return sent_msg
        except discord.NotFound:
            print(f"Failed to change role for {member} ({member.id}): member not found")
        except discord.Forbidden:
            print(
                f"Forbidden to change role for {member} ({member.id}); "
                f"possibly due to role hierarchy"
            )
        except discord.HTTPException as e:
            print(f"Failed to change role for {member} ({member.id}): {e.status} {e.code}")

    async def send_reminder(self, d):
        print(f"Sending reminder: {d}")
        channel = self.bot.get_channel(int(d['channel_id']))
        reminder_msg = d['msg_content']
        reminder_type = d['msg_type']
        reminder_interval = d['msg_interval']
        if (int(d['msg_type']) == 1):
            await self.send_msg(channel, reminder_msg, 0)
        elif (int(d['msg_type']) == 2):
            color = 0x00FF00
            if (d['embed_color']):
                # embed color is hex, 0x prefix
                color = d['embed_color']
            embed = discord.Embed(
                color=int(str(color), 16),
                description=(reminder_msg)
            )
            if (d['embed_title']):
                embed.set_author(name=d['embed_title'])
            if (d['thumbnail_icon']):
                embed.set_thumbnail(url=d['thumbnail_icon'])
            await self.send_msg(channel, embed, 1)

    @tasks.loop(seconds = 5)
    async def reminders(self):
        # TODO
        # Explain what is happening here.
        # Is there a better way to do this?
        for server_id in self.server_ids:
            user_reminders = await self.get_reminders(server_id)
            print(f'[API] {server_id} {len(user_reminders)} reminders found')
            if self.user_reminders[server_id] != user_reminders:
                self.user_reminders[server_id] = user_reminders
                for tup in self.loops:
                    tup[1].stop()
                self.loops = [(reminder, tasks.loop(seconds=reminder['msg_interval'])(self.send_reminder)) for reminder in self.user_reminders[server_id]]

    @tasks.loop(seconds = 1)
    async def bot_loops(self):
        # TODO
        # Explain what is happening here.
        # hint: how does it related to the above function?
        for tup in self.loops:
            if not tup[1].is_running():
                print(f"Not Found, Starting {tup[1]}")
                tup[1].start(tup[0])

    @tasks.loop(seconds=9.0)
    async def playing_status(self):
        await self.bot.change_presence(activity=discord.Game(name="Test Bot"))
        await asyncio.sleep(4)
        await self.bot.change_presence(activity=discord.Game(name="Botzie.com"))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.add_server(str(guild.id))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in {self.bot.user.id}")
        # initialize
        active_servers = self.bot.guilds
        for guild in active_servers:
            server_id = str(guild.id)
            self.add_server(server_id)
        # run tasks
        if not self.playing_status.is_running():
            self.playing_status.start()
        if not self.reminders.is_running():
            self.reminders.start()
        if not self.bot_loops.is_running():
            self.bot_loops.start()

async def bot_daemon():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    bot_description = f"Test Bot from Botzie.com"
    bot = commands.Bot(
        command_prefix='/',
        intents=intents,
        description = bot_description,
        help_command=None
    )
    async with bot:
        await bot.add_cog(Manager(bot))
        await bot.start(TOKEN)

def main():
    asyncio.run(bot_daemon())

main()
