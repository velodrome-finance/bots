import asyncio

import discord
from discord.ext import tasks

from .settings import BOT_TICKER_INTERVAL_MINUTES
from .data import Token, Price
from .helpers import LOGGER

class PriceBot(discord.Client):
    def __init__(self, *args, source_token: Token, target_token: Token, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_token = source_token
        self.target_token = target_token

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.ticker.start()

    async def on_ready(self):
        LOGGER.debug(f'Logged in as {self.user} (ID: {self.user.id})')
        LOGGER.debug('------')
        await self.update_presence(self.source_token.symbol)

    async def update_bot_member_nick(self, guild, nick: str):
        bot_member = await guild.fetch_member(self.user.id)
        if bot_member is None:
            return        
        await bot_member.edit(nick=nick)

    async def update_nick_for_all_servers(self, nick: str):
        await asyncio.gather(*map(lambda guild: self.update_bot_member_nick(guild, nick), self.guilds))

    async def update_presence(self, presence_text: str):
        # https://discordpy.readthedocs.io/en/latest/api.html#discord.ActivityType
        await self.change_presence(activity=discord.Activity(name=presence_text, type=discord.ActivityType.watching))

    @tasks.loop(seconds=BOT_TICKER_INTERVAL_MINUTES * 60)
    async def ticker(self):
        try:
            [source_token_price] = await Price.get_prices([self.source_token])
            await self.update_nick_for_all_servers(f"{self.target_token.symbol} {source_token_price.pretty_price}")
        except Exception as ex:
            LOGGER.error(f"Ticker failed with {ex}")

    @ticker.before_loop
    async def before_my_task(self):
        # wait until the bot logs in
        await self.wait_until_ready()
