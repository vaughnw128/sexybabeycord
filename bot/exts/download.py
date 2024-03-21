"""ytdl

Automatically converts youtube videos under 20 seconds
to mp4 files

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import re
from contextlib import redirect_stdout
from io import BytesIO

# external
import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands
from yt_dlp.utils import download_range_func

# project modules
from bot import constants

log = logging.getLogger("Download")

# link_regex = r"https:\/\/(www.|)youtu(be.com|.be)([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
link_regex = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"


class Download(commands.Cog):
    """Download class to handle ytdl-ing"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Download"""
        self.bot = bot
        self.download_menu = app_commands.ContextMenu(name="download", callback=self.download_menu)
        self.bot.tree.add_command(self.download_menu)

    @app_commands.command(name="download")
    async def download_command(
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

        if url is None:
            await interaction.followup.send("That message didn't have a youtube link")
            return

        # Gets the timestamp when it's passed through via the link as the start
        link_timestamp = re.search(r"\?t=(\d+)", link)

        # If tree for setting start and end times
        optional_arguments = None
        if start is not None and end is not None:
            start = convert_to_seconds(start)
            end = convert_to_seconds(end)
        elif link_timestamp is not None and end is not None:
            start = convert_to_seconds(link_timestamp.group(1))
            end = convert_to_seconds(end)
        elif link_timestamp is not None and end is None:
            start = convert_to_seconds(link_timestamp.group(1))
            end = start + 30
        elif start is not None:
            start = convert_to_seconds(start)
            end = start + 30

        # Optional arguments only if start and end are not none
        if start is not None and end is not None:
            optional_arguments = {
                "download_ranges": download_range_func(None, [(start, end)]),
                "force_keyframes_at_cuts": True,
            }

        video = await download(url.group(0), optional_arguments)
        await interaction.followup.send(file=discord.File(video, filename="sexybabey_download.mp4"))

    async def download_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Controls the download menu"""
        await interaction.response.defer()

        # Searches for the link regex from the message
        url = re.search(
            link_regex,
            message.content,
        )

        if url is None:
            await interaction.followup.send("That message didn't have a youtube link")
            return

        video = await download(url.group(0), None)
        await interaction.followup.send(file=discord.File(video, filename="sexybabey_download.mp4"))


def convert_to_seconds(minutes: str) -> int:
    """Converting XX:XX notation to seconds"""
    if ":" in minutes:
        split = minutes.split(":")
        seconds = int(split[0]) * 60 + int(split[1])
        return seconds
    else:
        return int(minutes)


def filename_hook(d):
    if d["status"] == "finished":
        os.rename(d["filename"], f"{constants.Bot.file_cache}outfile.mp4")


async def download(url, optional_args: dict | None) -> BytesIO:
    """Helper method for fixing links"""
    # Optional arguments for yt-dlp
    ydl_opts = {"format": "mp4", "outtmpl": "-", "logger": logging.getLogger()}

    # Add optional args if passed in from the clip mode
    if optional_args is not None:
        ydl_opts.update(optional_args)

    # Downloading the video
    buf = BytesIO()
    with redirect_stdout(buf):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
    buf.seek(0)
    return buf


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(Download(bot))
    log.info("Loaded")
