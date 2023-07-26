# Fate.py
# Twitter poster for james cage white tweets
# Very cool very swag, I like it
import re
import json

from discord.ext import commands, tasks
from twscrape import API, gather
from twscrape.logger import set_log_level
from bot import constants
import discord
from discord import app_commands
import logging

api = API()
set_log_level("CRITICAL")


class Fate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Initializes the cog.

        Parameters
        -----------
        bot: commands.Bot
            The bot object from the main cog runner.
        guild: discord.Guild
            The guild as specified in the config file.
        channel: disord.Channel
            The channel as specified in the config file.
        schedule_send: discord.ext.task
            Used to start the Discord task scheduler
        """

        self.bot = bot
        self.fate_task.start()

    @tasks.loop(minutes=5)
    async def fate_task(self):
        await self.fate()
    
    @app_commands.command(name="fate")
    async def fate_command(self, interaction: discord.Interaction):
        await self.fate()

    async def fate(self) -> None:
        fate_channel: discord.TextChannel = await self.bot.fetch_channel(constants.Channels.fate)

        """Handles the looping of the scrape_and_send() function."""
        recents = []
        async for message in fate_channel.history(limit=300):
            link = re.search(
                r"https:\/\/(fx|vx|)twitter.com([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
                message.content,
            )
            if link is not None:
                recents.append(int(link.group(0).split("/")[-1]))
        tweets = await gather(api.user_tweets(449700739, limit=20))
        for tweet in reversed(tweets):
            if tweet.id not in recents:
                await fate_channel.send(tweet.url.replace("twitter", "vxtwitter"))


async def setup(bot: commands.Bot):
    """Sets up the cog

    Parameters
    -----------
    bot: commands.Bot
        The main cog runners commands.Bot object
    """

    with open("bot/resources/accounts.json", "r") as f:
        accounts = json.load(f)
    
    for account in accounts:
        await api.pool.add_account(
            account['username'],
            account['password'],
            account['email'],
            account['email_password'],
            cookies=account['cookies']
        )

    accounts = await api.pool.accounts_info()

    await bot.add_cog(Fate(bot))
    logging.info("Fate loaded")
