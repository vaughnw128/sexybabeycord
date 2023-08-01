""" 
    Fate

    Automatically posts @JamesCageWhite's tweets in our
    #fate channel. Love this guy. Very cool very swag I like it

    Made with love and care by Vaughn Woerpel
"""

# built-in
import json
import logging
import re

# external
import discord
from discord.ext import commands, tasks
from twscrape import API, gather
from twscrape.logger import set_log_level

# project modules
from bot import constants

# Setting stuff for twscrape
api = API()
set_log_level("CRITICAL")

log = logging.getLogger("fate")


class Fate(commands.Cog):
    """Cog for running #fate"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the cog."""

        self.bot = bot
        self.fate_task.start()

    # Check James's twitter every 5 minutes
    @tasks.loop(minutes=5)
    async def fate_task(self) -> None:
        """Task loop just calling fate()"""
        await self.fate()

    async def fate(self) -> None:
        """Handles grabbing the tweets from twitter using twscrape"""

        fate_channel: discord.TextChannel = await self.bot.fetch_channel(
            constants.Channels.fate
        )

        # Reads messages in channel history to know what tweets can be sent
        try:
            recents = []
            async for message in fate_channel.history(limit=300):
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
            tweets = await gather(api.user_tweets(449700739, limit=20))
        except Exception:
            log.warning("Unable to gather tweets")
            return

        # Sends tweets that aren't in the recents
        num_tweets = 0
        for tweet in reversed(tweets):
            if tweet.id not in recents:
                await fate_channel.send(tweet.url.replace("twitter", "vxtwitter"))
                num_tweets += 1

        if num_tweets > 0:
            log.info(f"Sent {num_tweets} tweets from @JamesCageWhite")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    # Loads all accounts from json and adds them to the pool
    with open(constants.Fate.accounts, "r") as f:
        accounts = json.load(f)

    for count, account in enumerate(accounts):
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

    await bot.add_cog(Fate(bot))
    log.info("Loaded")
