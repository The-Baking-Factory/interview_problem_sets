#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Rahul Zalkikar

import os
import json
import daemon
import discord
import requests
import asyncio
import logging
import argparse
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = os.getenv('API_ENDPOINT_STOCKS_BY_TICKER')
API_KEY = os.getenv('API_KEY')

logging.basicConfig()
logger = logging.getLogger()
fh = logging.FileHandler("../logs/botlog", "a+")
logger.setLevel(logging.INFO)
logger.addHandler(fh)

class Manager(commands.Cog):
    def __init__(self, bot, ticker, name):
        self.bot = bot
        self.ticker = ticker
        self.name = name

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(color=0x00FF00)
        embed.set_author(name=f'{self.name} Price Help Page')
        embed.add_field(name='Name Update', value='31 min', inline=False)
        embed.add_field(name='Status Update', value='16 sec', inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        ticker_role = discord.utils.get(guild.roles, name=f"{self.name}-Manager") # get role
        if not ticker_role:
            ticker_role = await guild.create_role(name=f"{self.name}-Manager") # create role

        price_role = discord.utils.get(guild.roles, name=f"{self.name}-Price")
        if not price_role:
            price_role = await guild.create_role( name=f"{self.name}-Price")

        bot_member = guild.get_member(self.bot.user.id) # get bot member
        await bot_member.add_roles(ticker_role) # assign role to bot
        await bot_member.add_roles(price_role) # assign role to bot

        color = 0x00FF00
        if float(self.bot.last_price_change_in_name) < 0:
            color = 0xFF0000
        await price_role.edit(colour=color)

    @tasks.loop(minutes=31)
    async def update(self):
        color = 0x00FF00
        arrow = '⬈'
        if float(self.bot.last_price_change) < 0:
            color = 0xFF0000
            arrow = '⬊'
        try:
            await self.bot.user.edit(username=f"{self.name} {arrow} ${self.bot.last_price}")
            self.bot.last_price_change_in_name = self.bot.last_price_change
        except:
            logger.info("username update error")

        active_servers = self.bot.guilds
        for server in active_servers:
            try:
                guild = self.bot.get_guild(int(server.id))
            except:
                logger.info('guild error')
            try:
                role = discord.utils.get(guild.roles, name=f"{self.name}-Price")
            except:
                logger.info('role error')
            try:
                await role.edit(colour=color)
            except:
                logger.info('role edit error')

    @tasks.loop(seconds=16)
    async def activity(self):

        res = requests.request('GET', API_ENDPOINT+self.ticker, headers={'Authorization': API_KEY})
        data = res.json()[0]

        ratio_usd = str(data['ratio_usd'])
        marketcap_usd = data['marketcap_usd']
        price_change = data['price_change']
        high_24h = str(data['high_24h'])
        low_24h = str(data['low_24h'])
        short_ratio = str(data['short_ratio'])
        high_24h_change = str(data['high_24h_change'])
        low_24h_change = str(data['low_24h_change'])

        logger.info(f"Last price {self.ticker} = {ratio_usd}")
        logger.info(f"Last price change {self.ticker} = {price_change}")

        if ratio_usd != self.bot.last_price:
            self.bot.last_price = ratio_usd
        if price_change != self.bot.last_price_change:
            self.bot.last_price_change = price_change

        await self.bot.change_presence(activity=discord.Game(name=f"Price: ${ratio_usd}  [{price_change}%]"))
        await asyncio.sleep(3)
        await self.bot.change_presence(activity=discord.Game(name=f"MC: ${marketcap_usd}"))
        await asyncio.sleep(3)
        await self.bot.change_presence(activity=discord.Game(name=f"24h High: ${high_24h} [{high_24h_change}%]"))
        await asyncio.sleep(3)
        await self.bot.change_presence(activity=discord.Game(name=f"24h Low: ${low_24h} [{low_24h_change}%]"))
        await asyncio.sleep(3)
        await self.bot.change_presence(activity=discord.Game(name=f"Short Ratio: {short_ratio}"))

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('------')
        logger.info(f'Logged in {self.bot.user} (ID: {self.bot.user.id})')
        logger.info('------')

        res = requests.request('GET', API_ENDPOINT+self.ticker, headers={'Authorization': API_KEY})
        data = res.json()[0]

        ratio_usd = str(data['ratio_usd'])
        price_change = data['price_change']

        logger.info(f"Last price {self.ticker} = {ratio_usd}")
        logger.info(f"Last price change {self.ticker} = {price_change}")

        if ratio_usd != self.bot.last_price:
            self.bot.last_price = ratio_usd
        if price_change != self.bot.last_price_change:
            self.bot.last_price_change = price_change

        if not self.activity.is_running():
            self.activity.start()

        if not self.update.is_running():
            self.update.start()

async def bot_daemon(ticker, name, token):
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
    bot.last_price = ""
    bot.last_price_change = ""
    bot.last_price_change_in_name = ""
    async with bot:
        await bot.add_cog(Manager(bot, ticker, name))
        await bot.start(token)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--ticker',
                        required=True,
                        type=str)

    parser.add_argument('--name',
                        required=True,
                        type=str)

    parser.add_argument('--token',
                        required=True,
                        type=str)

    args = parser.parse_args()

    asyncio.run(bot_daemon(
        args.ticker,
        args.name,
        args.token
    ))

if __name__ == '__main__':
    main()
