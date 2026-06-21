# built-in
import logging
import re

# external
import discord
from discord.ext import commands

log = logging.getLogger("gloke")

gloke_regex = re.compile(r"\bgloke\b", re.IGNORECASE)
correction_message = "I think you mean goke!"


class Gloke(commands.Cog):
    """Deletes gloke messages and sends the author a correction."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Gloke cog."""

        self.bot = bot
        log.info("Gloke cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Correct messages containing the word gloke."""

        if message.author.bot:
            return

        for keyword in ("gloke", "gl0ke", "g1oke", "g10ke", "g10k3", "gl0k3", "g1ok3", "gloak", "g1oak"):
            if keyword in message.content.lower().replace(" ", ""):
                log.debug(f"Gloke keyword '{keyword}' detected from {message.author}")
                break

        log.debug(f"Gloke keyword detected from {message.author}")

        try:
            await message.delete()
            log.info(f"Deleted gloke message from {message.author}")
        except Exception as e:
            log.error(f"Failed to delete gloke message from {message.author}: {e}")
            return

        try:
            await message.author.send(correction_message)
            log.debug(f"Sent goke correction to {message.author}")
        except discord.Forbidden:
            await message.channel.send(f"{message.author.mention} {correction_message}", delete_after=30)
            log.debug(f"Sent fallback goke correction to {message.author}")
        except Exception as e:
            log.error(f"Failed to send goke correction to {message.author}: {e}")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog."""

    try:
        await bot.add_cog(Gloke(bot))
        log.info("Gloke cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load Gloke cog: {e}")
        raise
