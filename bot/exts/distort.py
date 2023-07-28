""" 
    Distort

    Allows for users to right click on images to distort them
    I like this one a lot.

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os

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
        self.distort_menu = app_commands.ContextMenu(
            name="distort", callback=self.distort_ctx
        )
        self.bot.tree.add_command(self.distort_menu)

    async def distort_ctx(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """Build the distort context menu"""

        await interaction.response.defer()

        # Grabs the file from the message and checks it
        fname = file_helper.grab(message)  # Grabs the image
        if fname is None:
            await interaction.followup.send(
                "An unexpected error occured while trying to fetch the image."
            )
            log.warning("Image was unable to be fetched")
            return

        # Checks file extension and distorts + sends
        if fname.endswith((".png", ".jpg", ".gif")):
            distorted = distort(fname)
            if distorted is not None:
                log.info(f"Image was succesfully distorted: {distorted})")
                await interaction.followup.send(file=discord.File(distorted))
                os.remove(distorted)
        else:
            log.info(f"Wrong filetype rejected: {fname})")
            await interaction.followup.send(
                "Silly fool! Distort doesn't work on that filetype"
            )
            os.remove(fname)


def distort(fname: str) -> str:
    """Handles the distortion using ImageMagick"""

    with Image(filename=fname) as temp_img:
        # Checks gif vs png/jpg
        if fname.endswith("gif"):
            with Image() as dst_image:
                with Image(filename=fname) as src_image:
                    # Coalesces and then distorts and puts the frame buffers into an output
                    src_image.coalesce()
                    for i, frame in enumerate(src_image.sequence):
                        frameimage = Image(image=frame)
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
                dst_image.save(filename=fname)
        else:
            # Simple distortion
            x, y = temp_img.width, temp_img.height
            temp_img.liquid_rescale(
                round(x * constants.Distort.ratio), round(y * constants.Distort.ratio)
            )
            temp_img.resize(x, y)
            temp_img.save(filename=fname)
    return fname


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Distort(bot))
    log.info("Loaded")
