"""
    Astropix

    Scrapes and sends the NASA picture of the day to our
    server's general chat. It's usually quite beautiful :>

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import urllib
from datetime import time
from io import BytesIO


# external
import aiohttp
import bs4 as bs
import discord
from discord import app_commands
from discord.ext import commands, tasks

# project modules
from bot import constants
from bot.utils import file_helper

log = logging.getLogger("astropix")


class Astropix(commands.Cog):
    """A Discord Cog to handle scraping and sending the NASA picture of the day."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the cog."""

        self.bot = bot
        self.schedule_send.start()

    @app_commands.command(name="fartypix")
    async def fartypix(self, interaction: discord.Interaction):
        file_bytes, alt = await scrape_astropix()
        file_bytes = file_bytes.read()
        ext = file_helper.get_file_extension(file_bytes)
        print(ext)
        await interaction.channel.send(
            content=f"Astronomy Picture of the Day!\n\n{alt}\n\nhttps://apod.nasa.gov/apod/astropix.html",
            file=discord.File(file_bytes, filename="astropix.png"),
        )

    @tasks.loop(time=time(hour=17))
    async def schedule_send(self) -> None:
        """Handles the looping of the scrape_and_send() function."""

        channel = await self.bot.fetch_channel(constants.Channels.general)

        file_bytes, alt = await scrape_astropix()
        await channel.send(
            content=f"Astronomy Picture of the Day!\n\n{alt}\n\nhttps://apod.nasa.gov/apod/astropix.html",
            file=discord.File(file_bytes, filename="astropix.png"),
        )
        log.info("Sent scheduled message")


async def scrape_astropix() -> tuple[BytesIO, str]:
    """Scrapes and sends the astronomy picture of the day."""

    # Grabs the page with a static link (literally has not changed since the 90s)
    html_page = urllib.request.urlopen("https://apod.nasa.gov/apod/astropix.html")
    soup = bs.BeautifulSoup(html_page, features="html.parser")
    images = []
    alt = ""

    # Finds the images on the page
    for img in soup.findAll("img", alt=True):
        images.append(img.get("src"))
        alt = img.get("alt")

    file_bytes = await file_helper.grab_file_bytes(f"http://apod.nasa.gov/{images[0]}")
    return file_bytes, alt


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    if constants.Channels.general is None:
        log.error(
            "General channel has not been specified in the environment variables. Aborting loading astrpix."
        )
        return

    await bot.add_cog(Astropix(bot))
    log.info("Loaded")
