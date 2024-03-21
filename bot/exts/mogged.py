"""
Tiny mogged feature, just to be silly!

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging

# external
import discord
from discord.ext import commands

log = logging.getLogger("Mogged")
keywords = ("byebye", "mogged", "mewing", "mewed", "looksmax")


class Mogged(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Mogged cog."""

        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Reacts with emojis on message."""

        for keyword in keywords:
            if keyword in message.content.lower().replace(" ", ""):
                await message.add_reaction("🤫")
                await message.add_reaction("🧏‍♂️")
                return


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Mogged(bot))
    log.info("Mogged")
