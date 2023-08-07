"""
    Gifify

    Allows users to right click videos and turn them into gifs

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging

# external
import discord
from discord import app_commands
from discord.ext import commands
from moviepy.editor import VideoFileClip
from wand.image import Image

# project modules
from bot.utils import file_helper, magick_helper

log = logging.getLogger("gifify")


class Gifify(commands.Cog):
    """Gifify class to handle all gabonga requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the Gifify class"""
        self.bot = bot

        self.gifify_menu = app_commands.ContextMenu(
            name="gifify", callback=self.gifify_menu
        )
        self.bot.tree.add_command(self.gifify_menu)

    async def gifify_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """Controls the gifify menu"""

        await interaction.response.defer()
        response = await gifify_helper(message)

        match response:
            case "Message had no file":
                await interaction.followup.send("That message didn't have a file!!")
                return
            case "Invalid filetype":
                await interaction.followup.send(
                    "Silly fool! gifify only works on video files!"
                )
                return
            case "Gifify failure":
                log.error(f"Failure while trying to Gifify video")
                await interaction.followup.send("Gifify has mysteriously failed")
                return

        log.info(f"Image was succesfully gififized: {response})")
        await interaction.followup.send(file=discord.File(response))
        file_helper.remove(response)


async def gifify_helper(message: discord.Message) -> str:
    """Helper method to help with gabonga requests"""

    # Grabs and checks file
    fname = file_helper.grab(message)
    if fname is None:
        return "Message had no file"

    # Checks filetype
    if not fname.endswith((".mp4", ".wav")):
        file_helper.remove(fname)
        return "Invalid filetype"

    videoClip = VideoFileClip(fname)
    fname = fname.split(".")[0] + ".gif"
    videoClip.write_gif(fname)

    if fname is not None:
        return fname
    else:
        file_helper.remove(fname)
        return "Gabonga failure"


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Gifify(bot))
    log.info("Loaded")
