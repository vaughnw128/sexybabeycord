"""Peanut Gallery

Automatically grabs a comment from whatever youtube link is sent,
then sends it to chat

Made with love and care by Vaughn Woerpel
"""

import json

# built-in
import logging
import random
import re
from contextlib import redirect_stdout

# external
import discord
import yt_dlp
from discord.ext import commands

# project


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


async def peanut(message: discord.Message) -> discord.Embed:
    """Helper method for grabbing comments"""
    # Searches for the link regex from the message
    link = re.search(
        link_regex,
        message.content,
    )

    if link is None:
        return None

    ydl_opts = {
        "extract_flat": "discard_in_playlist",
        "forcejson": True,
        "fragment_retries": 10,
        "getcomments": True,
        "ignoreerrors": "only_download",
        "noprogress": True,
        "postprocessors": [{"key": "FFmpegConcat", "only_multi_video": True, "when": "playlist"}],
        "quiet": True,
        "retries": 10,
        "simulate": True,
        "skip_download": True,
        "extractor_args": {"youtube": {"max_comments": ["100"]}},
    }

    info = ""
    with redirect_stdout(info):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(link.group(0))
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


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(PeanutGallery(bot))
    log.info("Loaded")
