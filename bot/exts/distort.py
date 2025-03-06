"""Distort

Allows for users to right click on images to distort them
I like this one a lot.

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
from io import BytesIO

# external
import discord
from discord import app_commands
from discord.ext import commands
from wand.image import Image

# project modules
from bot import constants
from bot.utils import file_helper

log = logging.getLogger("distort")


class Distort(commands.Cog):
    """A Discord Cog to handle image distortion"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the command context menu"""
        self.bot = bot
        self.distort_menu = app_commands.ContextMenu(name="distort", callback=self.distort_ctx)
        self.bot.tree.add_command(self.distort_menu)

    async def distort_ctx(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Build the distort context menu"""
        await interaction.response.defer()
        file, ext = await file_helper.grab_file(message)
        distorted = await distort(file, ext)

        await interaction.followup.send(file=discord.File(fp=distorted, filename=f"distort.{ext}"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'distort' it adds the caption to the image it's replying to"""
        if (
                not message.content.lower().startswith("distort")
                or message.author.id == self.bot.user.id
        ):
            return

        file, ext = await file_helper.grab_file(message)
        distorted = await distort(file, ext)

        await message.reply(file=discord.File(fp=distorted, filename=f"edited.{ext}"))

async def distort(file: BytesIO, ext: str) -> BytesIO:
    """Handles the distortion using ImageMagick"""
    buf = BytesIO()
    with Image(file=file) as src_image:
        if ext == "gif":
            src_image.coalesce()
            with Image() as dst_image:
                # Coalesces and then distorts and puts the frame buffers into an output
                for frame in src_image.sequence:
                    with Image(image=frame) as frameimage:
                        x, y = frame.width, frame.height
                        if x > 1 and y > 1:
                            frameimage.liquid_rescale(
                                round(x * constants.Distort.ratio),
                                round(y * constants.Distort.ratio),
                            )
                            frameimage.resize(x, y)
                            dst_image.sequence.append(frameimage)
                dst_image.optimize_layers()
                dst_image.optimize_transparency()
                dst_image.save(file=buf)
        else:
            # Simple distortion
            x, y = src_image.width, src_image.height
            src_image.liquid_rescale(round(x * constants.Distort.ratio), round(y * constants.Distort.ratio))
            src_image.resize(x, y)
            src_image.save(file=buf)

    buf.seek(0)
    return buf


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(Distort(bot))
    log.info("Loaded")
