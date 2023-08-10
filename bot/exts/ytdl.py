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
from yt_dlp.utils import download_range_func

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

    @app_commands.command(name="download")
    async def download(
        self,
        interaction: discord.Interaction,
        link: str,
        start: str | None,
        end: str | None,
    ):
        """Allows for downloading with commands"""

        await interaction.response.defer()

        # Searches for the link regex from the message
        url = re.search(
            link_regex,
            link,
        )

        optional_arguments = None
        if start is not None and end is not None:
            start = convert_to_seconds(start)
            end = convert_to_seconds(end)

            optional_arguments = {
                "download_ranges": download_range_func(None, [(start, end)]),
                "force_keyframes_at_cuts": True,
            }

        if url is None:
            await interaction.followup.send("That message didn't have a youtube link")
            return

        url = url.group(0)
        await ytdl_helper(interaction, url, optional_arguments)

    async def ytdl_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """Controls the ytdl menu"""

        await interaction.response.defer()

        # Searches for the link regex from the message
        url = re.search(
            link_regex,
            message.content,
        )

        if url is None:
            await interaction.followup.send("That message didn't have a youtube link")
            return

        url = url.group(0)
        await ytdl_helper(interaction, url, None)


def convert_to_seconds(minutes: str) -> int:
    """Converting XX:XX notation to seconds"""

    if ":" in minutes:
        split = minutes.split(":")
        seconds = int(split[0]) * 60 + int(split[1])
        return seconds
    else:
        return int(minutes)


async def ytdl_helper(
    interaction: discord.Interaction, url: str, optional_args: dict | None
):
    """Helper method for YTDL"""

    response = await ytdl(url, optional_args)

    match response:
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
    return response


def filename_hook(d):
    if d["status"] == "finished":
        os.rename(d["filename"], f"{constants.Bot.file_cache}outfile.mp4")


async def ytdl(url, optional_args: dict | None) -> None:
    """Helper method for fixing links"""

    # Optional arguments for yt-dlp
    ydl_opts = {
        "paths": {"home": constants.Bot.file_cache},
        "format": "mp4",
        "progress_hooks": [filename_hook],
    }

    # Add optional args if passed in from the clip mode
    if optional_args is not None:
        ydl_opts.update(optional_args)

    print(ydl_opts)
    # Downloading the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

        fname = f"{constants.Bot.file_cache}outfile.mp4"

        try:
            if file_helper.size_limit_exceeded(fname):
                file_helper.remove(fname)
                return "Size limit exceeded"
            return fname
        except Exception:
            file_helper.remove(fname)
            return "Ytdl failure"


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Ytdl(bot))
    log.info("Loaded")
