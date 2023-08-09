"""
    Gifify

    Allows users to right click videos and turn them into gifs

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import subprocess

# external
import discord
from discord import app_commands
from discord.ext import commands

from bot import constants

# project modules
from bot.utils import file_helper

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
            case "Size limit exceeded":
                log.error(f"File size exceeded")
                await interaction.followup.send(
                    "The resulting gif exceeded Discord filesize limits"
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
    """Helper method to help with gifify requests"""

    # Grabs and checks file
    fname = file_helper.grab(message)
    if fname is None:
        return "Message had no file"

    # Checks filetype
    if not fname.endswith((".mp4", ".wav")):
        file_helper.remove(fname)
        return "Invalid filetype"

    # Creates new filenames
    fname_in = f"{constants.Bot.file_cache}ffmpeg_in.{fname.split('.')[-1]}"
    fname_out = f"{constants.Bot.file_cache}ffmpeg_out.gif"

    # Rename the file to prevent OS command injection
    os.rename(fname, fname_in)
    subprocess.run(
        [f"ffmpeg -y -i {fname_in} -r 20 {fname_out} -loglevel quiet"], shell=True
    )
    file_helper.remove(fname_in)

    try:
        stats = os.stat(fname_out)
        file_size = stats.st_size / (1024 * 1024)
    except Exception:
        file_helper.remove(fname_out)
        return "Gifify failure"

    if file_size > 24.9:
        file_helper.remove(fname_out)
        return "Size limit exceeded"

    return fname_out


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Gifify(bot))
    log.info("Loaded")
