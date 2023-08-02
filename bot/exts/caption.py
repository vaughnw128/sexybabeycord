""" 
    Caption

    Adds captions to gifs and images with the old iFunny font

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import math
import os
import random
import re

# external
import discord
from discord import app_commands
from discord.ext import commands
from wand.color import Color
from wand.font import Font
from wand.image import Image

# project modules
from bot import constants
from bot.utils import file_helper, magick_helper

log = logging.getLogger("caption")


class Caption(commands.Cog):
    """Caption class to handle all caption requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the caption class """
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""

        # Checks caption and gets text
        if not message.content.startswith("caption") or not isinstance(message.reference, discord.message.MessageReference):
            return
        original_message = await message.channel.fetch_message(message.reference.message_id)
        
        caption_text = re.sub(r"^caption ", "", message.content)
        if len(caption_text) == 0:
            return

        # Checks for the author being the bot
        if message.author.id == constants.Bot.id:
            return

        # Grabs the file using reused distort bot code
        fname = file_helper.grab(original_message)
        if fname is None:
            return

        if fname is not None and fname.endswith((".png", ".jpg", ".gif")):

            captioned = await magick_helper.caption(fname, caption_text)

            if captioned is not None:
                await message.channel.send(
                    file=discord.File(captioned),
                )
            os.remove(captioned)
        else:
            os.remove(fname)


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Caption(bot))
    log.info("Loaded")
