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
from typing import Optional

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
        """Intializes the caption class"""
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""

        response = await caption_helper(message)

        match response:
            case "Message sent by self":
                return
            case "Message doesn't start with caption":
                return
            case "Message is not a reply":
                return
            case "No caption was specified":
                await message.reply("Looks like you didn't add a caption, buddy")
                return
            case "Original message had no file":
                await message.reply("Are you dumb? that's not even a file")
                return
            case "Invalid filetype":
                await message.reply("That's not an image or a gif :/")
                return
            case "Caption failure":
                log.error(f"Failure while trying to caption image/gif")
                await message.reply("Caption has mysteriously failed")
                return

        log.info(f"Image was succesfully captioned: {response})")
        await message.reply(file=discord.File(response))
        file_helper.remove(response)


async def caption_helper(message: discord.Message) -> str:
    """Helper method for captioning, allows for testing"""

    # Checks for the author being the bot
    if message.author.id == constants.Bot.id:
        return "Message sent by self"

    # Checks for the caption keyword
    if not message.content.startswith("caption"):
        return "Message doesn't start with caption"

    # Get original message if it is actually a message reply
    try:
        original_message = await message.channel.fetch_message(
            message.reference.message_id
        )
    except AttributeError:
        return "Message is not a reply"

    # Gets caption text
    caption_text = re.sub(r"^caption", "", message.content).strip()
    if caption_text is None or len(caption_text) == 0:
        return "No caption was specified"

    # Grabs and checks file
    fname = file_helper.grab(original_message)
    if fname is None:
        return "Original message had no file"

    # Checks filetype
    if not fname.endswith((".png", ".jpg", ".gif", ".jpeg")):
        file_helper.remove(fname)
        return "Invalid filetype"

    captioned = await magick_helper.caption(fname, caption_text)

    if captioned is not None:
        return captioned
    else:
        file_helper.remove(fname)
        return "Caption failure"


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Caption(bot))
    log.info("Loaded")
