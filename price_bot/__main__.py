import os
import asyncio

from typing import List

import discord
from discord.ext import tasks

from .settings import DISCORD_TOKEN, SOURCE_TOKEN_ADDRESS, STABLE_TOKEN_SYMBOL, BOT_TICKER_INTERVAL_MINUTES
from .data import Token, Price

class PriceBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.ticker.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

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
            source_token = await Token.get_by_token_address(SOURCE_TOKEN_ADDRESS)

            print(f"got source token {source_token}")

            [source_token_price] = await Price.get_prices([source_token])

            await self.update_nick_for_all_servers(f"{STABLE_TOKEN_SYMBOL} {source_token_price.pretty_price}")
            await self.update_presence(f"Velo {self.counter}")
            self.counter += 1
        except Exception as ex:
            print(f"Ticker failed with {ex}")

    @ticker.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

async def main():
    """Main function."""
    bot = PriceBot(intents=discord.Intents.default())
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())