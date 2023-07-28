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
import requests
import validators

# project modules
from bot import constants

log = logging.getLogger("file_helper")


def grab(message: discord.Message) -> str:
    """Grabs files from various types of discord messages"""

    url = None
    # Finds the URL that the image is at
    if message.embeds:
        # Checks if the embed itself is an image and grabs the url
        if message.embeds[0].video.proxy_url is not None:
            url = message.embeds[0].video.proxy_url
        elif (
            message.embeds[0].thumbnail.proxy_url is not None
            and "tenor" not in message.embeds[0].thumbnail.proxy_url
        ):
            url = message.embeds[0].thumbnail.proxy_url
        elif message.embeds[0].url is not None:
            url = message.embeds[0].url
        elif message.embeds[0].video.url is not None:
            url = message.embeds[0].video.url

    # Checks to see if the image is a message attachment
    elif message.attachments:
        url = message.attachments[0].url
    else:
        for item in message.content.split(" "):
            if validators.url(item):
                url = item

    if url is None:
        return None

    # Remove the trailing modifiers at the end of the link
    url = url.partition("?")[0]

    if "tenor" in url:
        id = url.split("-")[len(url.split("-")) - 1]
        resp = requests.get(
            f"https://tenor.googleapis.com/v2/posts?key={constants.Bot.tenor}&ids={id}&limit=1"
        )
        data = resp.json()
        url = data["results"][0]["media_formats"]["mediumgif"]["url"]

    fname = None
    if validators.url(url):
        try:
            fname = requests.utils.urlparse(url)
            fname = f"{constants.Bot.file_cache}{(os.path.basename(fname.path))}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with open(fname, "wb") as f:
                with urllib.request.urlopen(req) as r:
                    f.write(r.read())
            return fname
        except Exception:
            log.error("Unable to download file")
            return None
    else:
        log.error("Could not find a valid URL")
        return None
