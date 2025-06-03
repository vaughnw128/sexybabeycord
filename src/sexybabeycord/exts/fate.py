"""Fate

Automatically posts @JamesCageWhite's tweets in our
#fate channel. Love this guy. Very cool very swag I like it

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
from datetime import time

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

log = logging.getLogger("fate")


class Fate(commands.Cog):
    """Cog for running #fate"""

    def __init__(self, bot: commands.Bot, accounts: list) -> None:
        """Initializes the cog."""
        self.bot = bot
        self.accounts = accounts
        self.fate_task.start()
        self.relogin_task.start()

    # Check James's twitter every 5 minutes
    @tasks.loop(minutes=5)
    async def fate_task(self) -> None:
        """Task loop just calling fate()"""
        fate_channel: discord.TextChannel = await self.bot.fetch_channel(constants.Channels.fate)
        await self.fate(fate_channel, 449700739)
        # vx_underground_channel: discord.TextChannel = await self.bot.fetch_channel(constants.Channels.vx_underground)
        # await self.fate(vx_underground_channel, 1158139840866791424)

    @tasks.loop(time=time(hour=0))
    async def relogin_task(self) -> None:
        """Handles reloading accounts once per day to prevent de-auth issues"""
        await api.pool.relogin(self.accounts)
        log.info("Accounts re-logged in")

    async def fate(self, channel: discord.TextChannel, twitter_user: int) -> None:
        """Handles grabbing the tweets from twitter using twscrape"""

        # Reads messages in channel history to know what tweets can be sent
        try:
            recents = []
            async for message in channel.history(limit=300):
                link = re.search(
                    r"https:\/\/(fx|vx|)twitter.com([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
                    message.content,
                )
                if link is not None:
                    recents.append(int(link.group(0).split("/")[-1]))
        except Exception:
            log.warning("Unable to gather message history")
            return

        # Gathers tweets
        try:
            tweets = await gather(api.user_tweets(twitter_user, limit=20))
        except Exception:
            log.warning("Unable to gather tweets")
            return

        # Sends tweets that aren't in the recents
        num_tweets = 0
        for tweet in reversed(tweets):
            if tweet.id not in recents:
                await channel.send(
                    tweet.url.replace("https://twitter.com", "https://vxtwitter.com").replace(
                        "https://x.com", "https://vxtwitter.com"
                    )
                )
                num_tweets += 1

        if num_tweets > 0:
            log.info(f"Sent {num_tweets} tweets from @JamesCageWhite")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    if constants.Channels.fate is None:
        log.error("Fate channel has not been specified in the environment variables. Aborting loading fate.")
        return

    db = bot.database.TwitterAccounts
    cursor = db.find()
    for count, account in enumerate(cursor):
        await api.pool.add_account(
            account["username"],
            account["password"],
            account["email"],
            account["email_password"],
            cookies=account["cookies"],
        )
    log.info(f"Loaded {count} accounts")

    accounts = await api.pool.accounts_info()
    log.info("Added accounts to the pool")

    await bot.add_cog(Fate(bot, accounts))
    log.info("Loaded")
