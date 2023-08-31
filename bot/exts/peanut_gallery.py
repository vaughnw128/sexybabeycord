""" 
    Peanut Gallery

    Automatically grabs a comment from whatever youtube link is sent,
    then sends it to chat

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
import json
import random

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
            await message.reply(comment)

async def peanut(message: discord.Message) -> str:
    """Helper method for grabbing commentsa"""
    
    # Searches for the link regex from the message
    link = re.search(
        link_regex,
        message.content,
    )

    if link is None:
        return None
    
    optional_arguments = {
        "forcejson": True,
        "getcomments": True,
        "extractor_args": {
            "youtube": {
                "max_comments": "1000,all,100"
            }
        }
    }
    
    with yt_dlp.YoutubeDL(optional_arguments) as ydl:
        info = ydl.extract_info(link.group(0), download=False)
        
        if info['comments'] is None:
            return

        comment = random.choice(info['comments'])

    return comment['text']

async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(PeanutGallery(bot))
    log.info("Loaded")
