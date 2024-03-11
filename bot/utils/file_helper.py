"""
File_helper

Handles some useful stuff for working with files from discord

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
from pathlib import Path
from io import BytesIO

# external
import discord
from discord.app_commands import errors as discord_errors
import requests
import validators
from magika import Magika
import aiohttp

# project modules
from bot import constants

log = logging.getLogger("file_helper")
magika = Magika()

def get_file_extension(file: BytesIO | str) -> str | None:
    if isinstance(file, BytesIO):
        filetype = magika.identify_bytes(file.read()).dl.ct_label
        file.seek(0)
        return filetype
    elif isinstance(file, str):
        return magika.identify_path(Path(file)).dl.ct_label
    return None


async def grab_file(message: discord.Message) -> tuple[BytesIO, str]:
    """Grabs files from various types of discord messages"""
    # Grab all possible URLs
    urls = []
    if message.attachments:
        urls.append(message.attachments[0].url)
    if message.embeds:
        urls += [
            message.embeds[0].url,
            message.embeds[0].image.proxy_url,
            message.embeds[0].thumbnail.proxy_url,
        ]
    if message.content:
        for item in message.content.split(" "):
            if validators.url(item):
                urls.append(item)

    if len(urls) == 0:
        raise discord_errors.AppCommandError("No file found in the message.")
    url = [url for url in urls if url is not None][0]
    # Grabs tenor specific URL
    if "tenor" in url and ".gif" not in url:
        url = _get_tenor_url(url)
    return await grab_file_bytes(url)


def _get_tenor_url(url: str) -> str:
    if constants.Bot.tenor is None:
        log.error("No tenor token has been found in .env")
        raise discord_errors.AppCommandError("No tenor token was supplied. Please fix!")
    try:
        id = url.split("-")[-1]
        resp = requests.get(f"https://tenor.googleapis.com/v2/posts?key={constants.Bot.tenor}&ids={id}&limit=1")
        data = resp.json()
        url = data["results"][0]["media_formats"]["mediumgif"]["url"]
    except KeyError:
        log.error(f"Unable to get gif from tenor: {url}")
        raise discord_errors.AppCommandError("Unable to get gif from tenor.")
    return url


async def grab_file_bytes(url: str) -> tuple[BytesIO, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            buffer = BytesIO(await resp.read())
            ext = get_file_extension(buffer)
            return buffer, ext


def remove(fname: str) -> None:
    """Remove file if it exists"""

    if os.path.exists(fname):
        os.remove(fname)


def size_limit_exceeded(fname: str) -> bool:
    stats = os.stat(fname)
    file_size = stats.st_size / (1024 * 1024)

    if file_size > 24.9:
        return True
    return False
