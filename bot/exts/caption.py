"""
    Caption

    Adds captions to gifs and images with the old iFunny font

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
import math

# external
import discord
from discord.ext import commands
from wand.color import Color
from wand.font import Font
from wand.image import Image

# project modules
from bot.utils import file_helper

log = logging.getLogger("caption")


class Caption(commands.Cog):
    """Caption class to handle all caption requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the caption class"""
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""

        response = await self.caption_helper(message)

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


    async def caption_helper(self, message: discord.Message) -> str:
        """Helper method for captioning, allows for testing"""

        # Checks for the author being the bot
        if message.author.id == self.bot.user.id:
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

        try:
            captioned = await caption(fname, caption_text)
            return captioned
        except Exception:
            file_helper.remove(fname)
            return "Caption failure"


async def caption(fname: str, caption_text: str) -> str:
    """Adds a caption to images and gifs with image_magick"""

    with Image(filename=fname) as src_image:
        # Get height and width of image
        if fname.endswith(".gif"):
            x, y = src_image.sequence[0].width, src_image.sequence[0].height
        else:
            x, y = src_image.width, src_image.height

        font_size = round(64 * (x / 720))
        bar_height = int(math.ceil(len(caption_text) / 24) * (x / 8))
        if bar_height < 1:
            bar_height = 1
        font = Font(path="bot/resources/caption_font.otf", size=font_size)

        # Generate template image
        template_image = Image(
            width=x,
            height=y + bar_height,
            background=Color("white"),
        )

        template_image.caption(
            text=caption_text,
            gravity="north",
            font=font,
        )

        # Checks gif vs png/jpg
        if fname.endswith(".gif"):
            with Image() as dst_image:
                # Coalesces and then distorts and puts the frame buffers into an output
                src_image.coalesce()
                for framenumber, frame in enumerate(src_image.sequence):
                    with Image(image=template_image) as bg_image:
                        fwidth, fheight = frame.width, frame.height
                        if fwidth > 1 and fheight > 1:
                            bg_image.composite(frame, left=0, top=bar_height)
                            dst_image.sequence.append(bg_image)
                dst_image.optimize_layers()
                dst_image.optimize_transparency()
                dst_image.save(filename=fname)
        else:
            template_image.composite(src_image, left=0, top=bar_height)
            template_image.save(filename=fname)

    return fname

async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Caption(bot))
    log.info("Loaded")
