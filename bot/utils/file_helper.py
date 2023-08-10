"""
    File_helper

    Handles some useful stuff for working with files from discord

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import urllib

# external
import discord
import magic
import requests
import validators

# project modules
from bot import constants

log = logging.getLogger("file_helper")


def setup() -> None:
    """Remove file if it exists"""

    if not os.path.exists(constants.Bot.file_cache):
        os.makedirs(constants.Bot.file_cache)


def grab(message: discord.Message) -> str:
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
    url = url.partition("?")[0]

    # Handle tenor gifs
    if "tenor" in url and ".gif" not in url:
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
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

            # Downloads the file
            with open(fname, "wb") as f:
                with urllib.request.urlopen(req) as r:
                    f.write(r.read())

            # Adds a mime-type based file extension if it doesn't have one
            ext = os.path.splitext(fname)[-1].lower()
            if len(ext) == 0:
                mime_type = magic.from_file(fname, mime=True)
                new_fname = f"{fname}.{mime_type.split('/')[1]}"
                os.rename(fname, new_fname)
                fname = new_fname

            return fname
        except Exception:
            log.error(f"Unable to download file: {url}")
            return None
    else:
        log.error(f"Could not find a valid URL: {url}")
        return None


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
