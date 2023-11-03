"""
    Caption

    Adds captions to gifs and images with the old iFunny font

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import math
import re
import traceback

# external
import discord
from discord import app_commands
from discord.ext import commands
from wand.color import Color
from wand.font import Font
from wand.image import Image

# project modules
from bot.utils import file_helper

log = logging.getLogger("caption")


class AdvancedCaption(discord.ui.Modal, title="Caption"):
    name = discord.ui.TextInput(
        label="Caption",
        placeholder="Your caption here...",
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks for your feedback", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        log.error("Advanced caption modal unexpectedly errored out")
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )


class Caption(commands.Cog):
    """Caption class to handle all caption requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the caption class"""
        self.bot = bot
        self.advanced_caption = app_commands.ContextMenu(
            name="Advanced Caption", callback=self.advanced_caption_menu
        )
        self.bot.tree.add_command(self.advanced_caption)

    async def advanced_caption_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        await interaction.response.send_modal(AdvancedCaption())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""

        if (
            not message.content.startswith("caption")
            or message.author.id == self.bot.user.id
        ):
            return

        # Get original message if it is actually a message reply
        try:
            original_message = await message.channel.fetch_message(
                message.reference.message_id
            )
        except AttributeError:
            return
        fname = file_helper.grab(original_message)

        # Gets caption text
        caption_text = re.sub(r"^caption", "", message.content).strip()
        if caption_text is None or len(caption_text) == 0:
            await message.reply("Looks like you didn't add a caption, buddy")
            return None

        response = await caption_helper(message, fname, caption_text)

        log.info(f"Image was succesfully captioned: {response})")
        await message.reply(file=discord.File(response))
        file_helper.remove(response)


async def caption_helper(
    message: discord.Message, fname: str, caption_text: str
) -> str:
    """Helper method for captioning, allows for testing"""

    # Grabs and checks file

    if fname is None:
        await message.reply("Are you dumb? that's not even a file")
        return None

    # Checks filetype
    if not fname.endswith((".png", ".jpg", ".gif", ".jpeg")):
        file_helper.remove(fname)
        await message.reply("That's not an image or a gif :/")
        return None

    try:
        captioned = await caption(fname, caption_text)
        return captioned
    except Exception:
        file_helper.remove(fname)
        log.error(f"Failure while trying to caption image/gif")
        await message.reply("Caption has mysteriously failed")
        return None


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
