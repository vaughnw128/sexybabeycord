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

# project modules
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


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Distort(bot))
    log.info("Loaded")
