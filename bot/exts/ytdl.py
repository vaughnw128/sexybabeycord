"""
    ytdl

    Automatically converts youtube videos under 20 seconds
    to mp4 files

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import re

# external
import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands

# project modules
from bot import constants
from bot.utils import file_helper

log = logging.getLogger("ytdl")

link_regex = r"https:\/\/(www.|)youtu(be.com|.be)([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"


class Ytdl(commands.Cog):
    """Ytdl class to handle ytdl-ing"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Ytdl"""

        self.bot = bot
        self.ytdl_menu = app_commands.ContextMenu(name="ytdl", callback=self.ytdl_menu)
        self.bot.tree.add_command(self.ytdl_menu)

    async def ytdl_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """Controls the ytdl menu"""

        await interaction.response.defer()
        response = await ytdl(message)

        match response:
            case "Message had no Youtube link":
                await interaction.followup.send(
                    "That message didn't have a youtube link"
                )
                return
            case "Size limit exceeded":
                log.error(f"File size exceeded")
                await interaction.followup.send(
                    "The resulting video exceeded Discord filesize limits"
                )
                return
            case "Ytdl failure":
                log.error(f"Failure while trying to run Ytdl")
                await interaction.followup.send("Ytdl has mysteriously failed")
                return

        log.info(f"Youtube video was succesfully converted: {response})")
        await interaction.followup.send(file=discord.File(response))
        file_helper.remove(response)


def filename_hook(d):
    if d["status"] == "finished":
        os.rename(d["filename"], f"{constants.Bot.file_cache}outfile.mp4")


async def ytdl(message: discord.Message) -> None:
    """Helper method for fixing links"""

    # Searches for the link regex from the message
    link = re.search(
        link_regex,
        message.content,
    )

    if link is None:
        return "Message had no Youtube link"

    ydl_opts = {
        "paths": {"home": constants.Bot.file_cache},
        "format": "mp4",
        "progress_hooks": [filename_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(link.group(0), download=False)
        except Exception:
            return "Ytdl failure"

        sanitized = ydl.sanitize_info(info)

        fname = (
            f"{constants.Bot.file_cache}{sanitized['title']} [{sanitized['id']}].mp4"
        )

        ydl.download(link.group(0))

        fname = f"{constants.Bot.file_cache}outfile.mp4"

        try:
            stats = os.stat(fname)
            file_size = stats.st_size / (1024 * 1024)
        except Exception:
            file_helper.remove(fname)
            return "Ytdl failure"

        if file_size > 24.9:
            file_helper.remove(fname)
            return "Size limit exceeded"

        return fname


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Ytdl(bot))
    log.info("Loaded")
