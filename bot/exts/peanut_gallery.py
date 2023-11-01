"""
    Peanut Gallery

    Automatically grabs a comment from whatever youtube link is sent,
    then sends it to chat

    Made with love and care by Vaughn Woerpel
"""

import json

# built-in
import logging
import random
import re
import subprocess

# external
import discord
import yt_dlp
from discord.ext import commands

# project modules
log = logging.getLogger("peanut-gallery")

link_regex = r"https:\/\/(www.|)youtu(be.com|.be)([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"


class PeanutGallery(commands.Cog):
    """Fixlink class to handle the... fixing of links"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize peanut_gallery"""

        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Grab comment on link matching the regex"""

        comment = await peanut(message)
        if comment is not None:
            await message.reply(embed=comment)


async def peanut(message: discord.Message) -> str:
    """Helper method for grabbing commentsa"""

    # Searches for the link regex from the message
    link = re.search(
        link_regex,
        message.content,
    )

    if link is None:
        return None
    try:
        info = subprocess.check_output(
            f"yt-dlp --skip-download --write-comments --extractor-args \"youtube:max_comments='100,100,0,0'\" {link.group(0)} -j",
            shell=True,
        ).decode()
        info = json.loads(info)

        if info["comments"] is None:
            return None

        comment = random.choice(info["comments"])

        embed = discord.Embed(title="", description=comment["text"])
        embed.set_author(
            name=comment["author"],
            url=comment["author_url"],
            icon_url=comment["author_thumbnail"],
        )

        return embed
    except Exception:
        return None


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(PeanutGallery(bot))
    log.info("Loaded")
