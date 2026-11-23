"""Tiny mogged feature, just to be silly!

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging

# external
import discord
from discord.ext import commands

log = logging.getLogger("Mogged")
keywords: tuple[str, ...] = ("byebye", "mogged", "mewing", "mewed", "looksmax")


class Mogged(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Mogged cog."""
        self.bot = bot
        log.info("Mogged cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Reacts with emojis on message."""
        if message.author.bot:
            return

        for keyword in keywords:
            if keyword in message.content.lower().replace(" ", ""):
                log.debug(f"Mogged keyword '{keyword}' detected from {message.author}")
                try:
                    await message.add_reaction("🤫")
                    await message.add_reaction("🧏‍♂️")
                    log.debug(f"Added mogged reactions to message from {message.author}")
                except Exception:
                    log.exception("Failed to add mogged reactions")
                return


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(Mogged(bot))
        log.info("Mogged cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load Mogged cog: {e}")
        raise
