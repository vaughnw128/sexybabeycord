""" 
    Caption

    Adds captions to gifs and images with the old iFunny font

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import random
import re
import math

# external
import discord
from discord import app_commands
from discord.ext import commands
from wand.image import Image
from wand.color import Color
from wand.font import Font

# project modules
from bot import constants
from bot.utils import file_helper

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

            captioned = caption(fname, caption_text)

            if captioned is not None:
                await message.channel.send(
                    file=discord.File(captioned),
                )
            os.remove(captioned)
        else:
            os.remove(fname)


def caption(fname: str, caption_text: str) -> str:
    """Adds a caption to images and gifs with image_magick"""
    try:
        with Image(filename=fname) as temp_img:
            x, y = temp_img.width, temp_img.height
            font_size = round(64 * (x/720))
            bar_height = int(math.ceil(len(caption_text)/25) * (x/8))
            if bar_height < 1: bar_height = 1 
            font = Font(path="bot/resources/caption_font.otf", size=font_size)

            # Checks gif vs png/jpg
            if fname.endswith("gif"):
                with Image() as dst_image:
                    with Image(filename=fname) as src_image:
                        # Coalesces and then distorts and puts the frame buffers into an output
                        src_image.coalesce()
                        for frame in src_image.sequence:
                            with Image(image=frame) as frameimage:
                                x, y = frame.width, frame.height
                                if x > 1 and y > 1:
                                    with Image(width = x, height = y + bar_height, background=Color("white")) as bg_image:
                                        bg_image.composite(frameimage, left = 0, top = bar_height)
                                        bg_image.caption(text=caption_text, gravity="north", font=font)
                                        dst_image.sequence.append(bg_image)
                    dst_image.optimize_layers()
                    dst_image.optimize_transparency()
                    dst_image.save(filename=fname)
            else:
                with Image(width = x, height = y + bar_height, background=Color("white")) as bg_image:
                    bg_image.composite(temp_img, left = 0, top = bar_height)
                    bg_image.caption(text=caption_text, gravity="north", font=font)
                    bg_image.save(filename=fname)
    
        return fname
    except Exception:
        return None

    

async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Caption(bot))
    log.info("Loaded")
