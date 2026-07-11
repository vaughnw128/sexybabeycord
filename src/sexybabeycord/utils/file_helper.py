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
import aiobotocore.session
from botocore.config import Config

# external
import discord
from discord.app_commands import errors as discord_errors
from magika import Magika

log = logging.getLogger("file_helper")
magika = Magika()

_BUCKET = "cdn"
_CDN_BASE = "https://cdn.vaughn.sh"
_ENDPOINT = "http://garage.applications.svc.cluster.local:3900"

_botocore_session = aiobotocore.session.get_session()
_S3_CONFIG = Config(signature_version="s3v4", s3={"addressing_style": "path"})

# Both lazily initialised on first upload so they bind to the bot's event loop.
_s3_client = None


async def _get_s3_client():
    global _s3_client
    if _s3_client is None:
        ctx = _botocore_session.create_client(
            "s3",
            endpoint_url=_ENDPOINT,
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY_ID").strip(),
            aws_secret_access_key=os.getenv("MINIO_SECRET_ACCESS_KEY").strip(),
            region_name="garage",
            config=_S3_CONFIG,
        )
        _s3_client = await ctx.__aenter__()
    return _s3_client


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


def find_media_url(message) -> str | None:
    """Return the best downloadable media URL exposed by a Discord message."""

    urls: list[str | None] = []
    if message.attachments:
        attachment = message.attachments[0]
        urls.extend((getattr(attachment, "proxy_url", None), attachment.url))

    for embed in message.embeds:
        image = getattr(embed, "image", None)
        thumbnail = getattr(embed, "thumbnail", None)
        urls.extend(
            (
                getattr(image, "proxy_url", None),
                getattr(image, "url", None),
                getattr(thumbnail, "proxy_url", None),
                getattr(thumbnail, "url", None),
                getattr(embed, "url", None),
            )
        )

    if message.content:
        urls.extend(item for item in message.content.split() if item.startswith(("https://", "http://")))

    return next((url for url in urls if url), None)


async def grab_file(message: discord.Message) -> tuple[BytesIO, str]:
    """Grabs files from various types of discord messages"""

    url = find_media_url(message)
    if url is None:
        raise discord_errors.AppCommandError("No file found in the message.")
    return await grab_file_bytes(url)


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


async def cdn_upload(data: BytesIO, ext: str) -> str:
    """Upload bytes to the CDN and return the public URL."""

    fname = str(uuid.uuid4()) + "." + ext
    client = await _get_s3_client()
    data.seek(0)
    await client.put_object(Bucket=_BUCKET, Key=fname, Body=data.read())
    return f"{_CDN_BASE}/{fname}"
