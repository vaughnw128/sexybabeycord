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
from sexybabeycord import constants
from sexybabeycord.utils import file_helper

log = logging.getLogger("distort")


class Distort(commands.Cog):
    """A Discord Cog to handle image distortion"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the command context menu"""
        self.bot = bot
        self.distort_menu = app_commands.ContextMenu(name="distort", callback=self.distort_ctx)
        self.bot.tree.add_command(self.distort_menu)
        log.info("Distort cog initialized")

    async def distort_ctx(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Build the distort context menu"""
        log.debug(f"Distort request from {interaction.user} for message {message.id}")
        await interaction.response.defer()

        try:
            file, ext = await file_helper.grab_file(message)
            log.debug(f"Retrieved file with extension: {ext}")

            distorted = await distort(file, ext)
            log.debug("Successfully distorted image")

            location = file_helper.cdn_upload(distorted, ext)
            await interaction.followup.send(content=location)
            log.info(f"Successfully processed distort request for user {interaction.user}")

        except Exception as e:
            log.error(f"Distort processing failed: {e}")
            raise

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'distort' it adds the caption to the image it's replying to"""
        if not message.content.lower().startswith("distort") or message.author.id == self.bot.user.id:
            return

        log.debug(f"Distort command from {message.author} in {message.channel}")

        try:
            file, ext = await file_helper.grab_file(message)
            distorted = await distort(file, ext)
            location = file_helper.cdn_upload(distorted, ext)
            await message.reply(content=location)
            log.info(f"Successfully processed distort command for user {message.author}")
        except Exception as e:
            log.error(f"Distort command failed: {e}")
            await message.reply("Failed to distort image")


async def distort(file: BytesIO, ext: str) -> BytesIO:
    """Handles the distortion using ImageMagick"""
    log.debug(f"Starting distortion for file with extension: {ext}")
    buf = BytesIO()

    try:
        with Image(file=file) as src_image:
            if ext == "gif":
                log.debug("Processing GIF distortion")
                src_image.coalesce()
                with Image() as dst_image:
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
                log.debug("GIF distortion completed successfully")
            else:
                log.debug("Processing static image distortion")
                x, y = src_image.width, src_image.height
                src_image.liquid_rescale(round(x * constants.Distort.ratio), round(y * constants.Distort.ratio))
                src_image.resize(x, y)
                src_image.save(file=buf)
                log.debug("Static image distortion completed successfully")

        buf.seek(0)
        return buf

    except Exception as e:
        log.error(f"Distortion failed: {e}")
        raise


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(Distort(bot))
        log.info("Distort cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load Distort cog: {e}")
        raise
