""" Astropix (A Sexybabeycord Cog)

    This cog is an isolated portion of the main Sexybabeycord bot.
    It's primary function is to scrape and send the NASA picture of the day
    to our server's general chat. It's usually quite beautiful :>

    Made with love and care by Vaughn Woerpel
"""

import io
import urllib
from datetime import time
import logging

import aiohttp
import bs4 as bs
import discord
from discord.ext import commands, tasks
from bot import constants

class Astropix(commands.Cog):
    """ A Discord Cog to handle scraping and sending the NASA picture of the day. """

    def __init__(self, bot: commands.Bot):
        """ Initializes the cog. """

        self.bot = bot
        self.channel = self.bot.fetch_channel(constants.Channels.yachts)
        self.schedule_send.start()

    async def scrape_and_send(self):
        """ Scrapes and sends the astronomy picture of the day. """

        # Grabs the page with a static link (literally has not changed since the 90s)
        html_page = urllib.request.urlopen("https://apod.nasa.gov/apod/astropix.html")
        soup = bs.BeautifulSoup(html_page)
        images = []
        alt = ""

        # Finds the images on the page
        for img in soup.findAll("img", alt=True):
            images.append(img.get("src"))
            alt = img.get("alt")

        # Grabs the image based on the image URL and converts to a Discord file object
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://apod.nasa.gov/{images[0]}") as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await self.channel.send(
                        content=f"Astronomy Picture of the Day!\n\n{alt}\n\nhttps://apod.nasa.gov/apod/astropix.html",
                        file=discord.File(file, "astropic.jpg"),
                    )

    @tasks.loop(time=time(hour=16))
    async def schedule_send(self):
        """ Handles the looping of the scrape_and_send() function. """

        await self.scrape_and_send()


async def setup(bot: commands.Bot):
    """ Sets up the cog """

    await bot.add_cog(Astropix(bot))
    logging.info("Astropix loaded")
