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
from bot.utils import file_helper, magick_helper

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
        response = await distort_helper(message)

        match response:
            case "Message had no file":
                interaction.followup.send("That message didn't have a file!!")
                return
            case "Invalid filetype":
                await interaction.followup.send(
                    "Silly fool! Distort doesn't work on that filetype"
                )
                return
            case "Distort failure":
                log.error(f"Failure while trying to distort image/gif")
                await interaction.followup.send("Distortion has mysteriously failed")
                return

        log.info(f"Image was succesfully distorted: {response})")
        await interaction.followup.send(file=discord.File(response))
        file_helper.remove(response)


async def distort_helper(message: discord.Message) -> str:
    """Helper method for distorting, allows for testing"""

    # Grabs and checks file
    fname = file_helper.grab(message)
    if fname is None:
        return "Message had no file"

    # Checks filetype
    if not fname.endswith((".png", ".jpg", ".gif", ".jpeg")):
        file_helper.remove(fname)
        return "Invalid filetype"

    distorted = await magick_helper.distort(fname)

    if distorted is not None:
        return distorted
    else:
        file_helper.remove(fname)
        return "Distort failure"

async def distort(fname: str) -> str:
    """Handles the distortion using ImageMagick"""

    with Image(filename=fname) as src_image:
        # Checks gif vs png/jpg
        if fname.endswith("gif"):
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
                dst_image.save(filename=fname)
        else:
            # Simple distortion
            x, y = src_image.width, src_image.height
            src_image.liquid_rescale(
                round(x * constants.Distort.ratio), round(y * constants.Distort.ratio)
            )
            src_image.resize(x, y)
            src_image.save(filename=fname)
    return fname

async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Distort(bot))
    log.info("Loaded")
