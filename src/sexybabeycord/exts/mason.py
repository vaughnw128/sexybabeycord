"""Tiny mason feature, just to be silly!

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
from typing import Tuple

# external
import discord
from discord.ext import commands

log = logging.getLogger("Mason")
keywords: Tuple[str, ...] = ("can you", "water my", "mason")


class Mason(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Mason cog."""
        self.bot = bot
        log.info("Mason cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Reacts with emojis on message."""
        if message.author.bot:
            return

        for keyword in keywords:
            if keyword in message.content.lower().replace(" ", ""):
                log.debug(f"Mason keyword '{keyword}' detected from {message.author}")
                try:
                    await message.add_reaction("<:mason:1440438650855755859>")
                    log.debug(f"Added mason reaction to message from {message.author}")
                except Exception as e:
                    log.error(f"Failed to add mason reactions: {e}")
                return


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(Mason(bot))
        log.info("Mason cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load Mason cog: {e}")
        raise
