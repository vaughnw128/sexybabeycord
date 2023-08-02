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
            distorted = await magick_helper.distort(fname)
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


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Distort(bot))
    log.info("Loaded")
