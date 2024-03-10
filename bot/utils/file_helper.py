"""
    File_helper

    Handles some useful stuff for working with files from discord

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import shutil
from pathlib import Path
from io import BytesIO

# external
import discord
import requests
import validators
from magika import Magika
import aiohttp

# project modules
from bot import constants

log = logging.getLogger("file_helper")


def setup() -> None:
    """Remove file if it exists"""

    if not os.path.exists(constants.Bot.file_cache):
        os.makedirs(constants.Bot.file_cache)


def get_file_extension(file: BytesIO | str) -> str:
    magika = Magika()
    if isinstance(file, BytesIO):
        return magika.identify_bytes(file.read()).dl.ct_label
    elif isinstance(file, str):
        return magika.identify_path(Path(file)).dl.ct_label
    return None


def grab(message: discord.Message) -> str | None:
    """Grabs files from various types of discord messages"""

    url = None
    # Finds the URL that the image is at
    if message.embeds:
        # Checks if the embed itself is an image and grabs the url
        if "tenor" in message.embeds[0].url:
            url = message.embeds[0].url
        elif message.embeds[0].thumbnail.proxy_url:
            url = message.embeds[0].thumbnail.proxy_url
    # Checks to see if the image is a message attachment
    elif message.attachments:
        url = message.attachments[0].url

    # Otherwise just grab URL
    else:
        for item in message.content.split(" "):
            if validators.url(item):
                url = item

    # If there isn't a url, return None
    if url is None:
        return None

    # Remove the trailing modifiers at the end of the link
    return download_url(url)


def download_url(url: str) -> str | None:
    # Handle tenor gifs
    if "tenor" in url and ".gif" not in url:
        if constants.Bot.tenor is None:
            log.error(f"No tenor token has been found in .env")
            return None
        try:
            id = url.split("-")[-1]
            resp = requests.get(
                f"https://tenor.googleapis.com/v2/posts?key={constants.Bot.tenor}&ids={id}&limit=1"
            )
            data = resp.json()
            url = data["results"][0]["media_formats"]["mediumgif"]["url"]
        except KeyError:
            log.error(f"Unable to get gif from tenor: {url}")
            return None

    fname = None
    if validators.url(url):
        try:
            fname = requests.utils.urlparse(url)
            fname = f"{constants.Bot.file_cache}{(os.path.basename(fname.path))}"

            # Downloads the file
            with requests.get(url, stream=True) as r:
                with open(fname, "wb") as f:
                    shutil.copyfileobj(r.raw, f)

            # Adds a mime-type based file extension if it doesn't have one
            ext = os.path.splitext(fname)[-1].lower()
            if len(ext) == 0:
                new_fname = f"{fname}.{get_file_extension(fname)}"
                os.rename(fname, new_fname)
                fname = new_fname

            return fname
        except Exception:
            log.error(f"Unable to download file: {url}")
            return None
    else:
        log.error(f"Could not find a valid URL: {url}")
        return None

async def grab_file_bytes(url: str) -> BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            buffer = BytesIO(await resp.read())
            return buffer


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
