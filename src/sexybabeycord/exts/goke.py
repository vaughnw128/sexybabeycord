# built-in
import logging
import random

# external
import discord
from discord.ext import commands

log = logging.getLogger("gloke")

correction_message = "Hey there! It looks like you mentioned 'gloke' in some form. I think you meant GOKE!"
epithets = (
    "Goke will cleanse us all with his holy light!",
    "Glory to goke!",
    "Hail goke!",
    "All heretics shall be purged in the name of goke!",
    "Bow before goke's glory!",
    "Goke will save us all!",
    "Goke is the one true god!",
    "Goke's light will guide us!",
    "Goke will protect us from the darkness!",
)


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

        found = False
        for keyword in ("gloke", "gl0ke", "g1oke", "g10ke", "g10k3", "gl0k3", "g1ok3", "gloak", "g1oak", "gløke"):
            if keyword in message.content.lower().replace(" ", ""):
                log.debug(f"Gloke keyword '{keyword}' detected from {message.author}")
                found = True
                break

        if not found:
            return

        log.debug(f"Gloke keyword detected from {message.author}")

        try:
            await message.delete()
            log.info(f"Deleted gloke message from {message.author}")
        except Exception as e:
            log.error(f"Failed to delete gloke message from {message.author}: {e}")
            return

        try:
            await message.author.send(correction_message + " " + epithets[random.randint(0, len(epithets) - 1)])
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
