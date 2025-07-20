"""Fate

Automatically posts @JamesCageWhite's tweets in our
#fate channel. Love this guy. Very cool very swag I like it

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
from datetime import time
from typing import List

# external
import discord
from discord.ext import commands, tasks
from twscrape import API, gather
from twscrape.logger import set_log_level

# project modules
from sexybabeycord import constants

# Setting stuff for twscrape
api = API()
set_log_level("CRITICAL")

# Suppress HTTP request logging from various libraries that twscrape uses
# This prevents spam in logs from the frequent Twitter API requests
http_loggers = [
    "httpx",
    "urllib3",
    "requests",
    "aiohttp",
    "asyncio",
    "httpcore",
    "twscrape",
    "twscrape.api",
    "twscrape.logger",
    "twscrape.utils",
    "twscrape.models",
    "twscrape.queue",
]

for logger_name in http_loggers:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

log = logging.getLogger("fate")


class Fate(commands.Cog):
    """Cog for running #fate"""

    def __init__(self, bot: commands.Bot, accounts: List) -> None:
        """Initializes the cog."""
        self.bot = bot
        self.accounts = accounts
        self.fate_task.start()
        self.relogin_task.start()
        log.info(f"Fate cog initialized with {len(accounts)} accounts")

    @tasks.loop(minutes=5)
    async def fate_task(self) -> None:
        """Task loop just calling fate()"""
        try:
            fate_channel: discord.TextChannel = await self.bot.fetch_channel(constants.Channels.fate)
            await self.fate(fate_channel, 449700739)
            log.debug("Fate task completed successfully")
        except Exception as e:
            log.error(f"Fate task failed: {e}")

    @tasks.loop(time=time(hour=0))
    async def relogin_task(self) -> None:
        """Handles reloading accounts once per day to prevent de-auth issues"""
        try:
            await api.pool.relogin(self.accounts)
            log.info(f"Successfully re-logged in {len(self.accounts)} accounts")
        except Exception as e:
            log.error(f"Failed to re-login accounts: {e}")

    async def fate(self, channel: discord.TextChannel, twitter_user: int) -> None:
        """Handles grabbing the tweets from twitter using twscrape"""
        log.debug(f"Starting fate check for user {twitter_user} in channel {channel.name}")

        try:
            recents = []
            async for message in channel.history(limit=300):
                link = re.search(
                    r"https:\/\/(fx|vx|)twitter.com([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
                    message.content,
                )
                if link is not None:
                    recents.append(int(link.group(0).split("/")[-1]))
            log.debug(f"Found {len(recents)} recent tweets in channel history")
        except Exception as e:
            log.warning(f"Unable to gather message history: {e}")
            return

        try:
            tweets = await gather(api.user_tweets(twitter_user, limit=20))
            log.debug(f"Retrieved {len(tweets)} tweets from Twitter API")
        except Exception as e:
            log.warning(f"Unable to gather tweets: {e}")
            return

        num_tweets = 0
        for tweet in reversed(tweets):
            if tweet.id not in recents:
                await channel.send(
                    tweet.url.replace("https://twitter.com", "https://vxtwitter.com").replace(
                        "https://x.com", "https://vxtwitter.com"
                    )
                )
                num_tweets += 1
                log.debug(f"Posted tweet {tweet.id} to channel")

        if num_tweets > 0:
            log.info(f"Successfully posted {num_tweets} new tweets from @JamesCageWhite")
        else:
            log.debug("No new tweets to post")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    log.info("Setting up Fate cog...")

    if constants.Channels.fate is None:
        log.error("Fate channel has not been specified in the environment variables. Aborting loading fate.")
        return

    try:
        db = bot.database.TwitterAccounts
        cursor = db.find()
        count = 0

        for count, account in enumerate(cursor):
            try:
                await api.pool.add_account(
                    account["username"],
                    account["password"],
                    account["email"],
                    account["email_password"],
                    cookies=account["cookies"],
                )
                log.debug(f"Added account {account['username']} to pool")
            except Exception as e:
                log.error(f"Failed to add account {account.get('username', 'unknown')}: {e}")

        log.info(f"Successfully loaded {count} Twitter accounts")

        accounts = await api.pool.accounts_info()
        log.info(f"Added {len(accounts)} accounts to the pool")

        await bot.add_cog(Fate(bot, accounts))
        log.info("Fate cog loaded successfully")

    except Exception as e:
        log.error(f"Failed to setup Fate cog: {e}")
        raise
