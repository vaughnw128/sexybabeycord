"""File_helper

Handles some useful stuff for working with files from discord

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import uuid
from io import BytesIO
from pathlib import Path

import aiohttp

# external
import discord
import requests
import validators
from discord.app_commands import errors as discord_errors
from magika import Magika
from minio import Minio

# project modules
from sexybabeycord import constants

log = logging.getLogger("file_helper")
magika = Magika()

minio_client = Minio(
    "s3.vaughn.sh", access_key=os.getenv("MINIO_ACCESS_KEY_ID").strip(), secret_key=os.getenv("MINIO_SECRET_ACCESS_KEY").strip(), region="us-east"
)


def get_file_extension_from_bytes(file: BytesIO | str) -> str:
    if isinstance(file, BytesIO):
        filetype = magika.identify_bytes(file.read()).filetype.dl.ct_label
        file.seek(0)
        return filetype
    elif isinstance(file, str):
        return magika.identify_path(Path(file)).dl.ct_label
    raise ValueError


def get_file_extension_from_url(url: str) -> str | None:
    try:
        return url.split("?")[0].split(".")[-1]
    except IndexError:
        return None


async def grab_file(message: discord.Message) -> tuple[BytesIO, str]:
    """Grabs files from various types of discord messages"""
    # Grab all possible URLs
    urls = []
    if message.attachments:
        urls.append(message.attachments[0].url)
    if message.embeds:
        if message.embeds[0].url.startswith("https://cdn.discordapp.com"):
            urls += [message.embeds[0].thumbnail.proxy_url]
        else:
            urls += [
                message.embeds[0].url,
                message.embeds[0].thumbnail.proxy_url,
                message.embeds[0].image.proxy_url,
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


def check_discord_file_timeout(buffer):
    if buffer.read() == b"This content is no longer available.":
        raise ValueError("The Discord file has timed out.")
    else:
        buffer.seek(0)


async def grab_file_bytes(url: str) -> tuple[BytesIO, str]:
    """Grabs the bytes of a file from the URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            buffer = BytesIO(await resp.read())

            # Handle if the discord file has timed out due to discord file timing query headers
            try:
                check_discord_file_timeout(buffer)
            except ValueError:
                raise discord_errors.AppCommandError("Unable to pull the filetype from the buffer.")
            # First checks the URL file extension, then pulls it from the file buffer
            try:
                return buffer, get_file_extension_from_url(url)
            except ValueError:
                return buffer, get_file_extension_from_bytes(buffer)


def remove(filename: str) -> None:
    """Remove file if it exists"""
    if os.path.exists(filename):
        os.remove(filename)


def cdn_upload(bytes: BytesIO, ext: str) -> str:
    bytes_size = bytes.getbuffer().nbytes
    bytes.seek(0)
    fname = str(uuid.uuid4()) + "." + ext
    response = minio_client.put_object("cdn", fname, bytes, bytes_size)
    return f"https://s3.vaughn.sh/cdn/{response._object_name}"
