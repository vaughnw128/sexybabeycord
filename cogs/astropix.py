""" Astropix (A Sexybabeycord Cog)

    This cog is an isolated portion of the main Sexybabeycord bot.
    It's primary function is to scrape and send the NASA picture of the day
    to our server's general chat. It's usually quite beautiful :>

    Made with love and care by Vaughn Woerpel
"""

import io
import os
import urllib
from datetime import time

import aiohttp
import bs4 as bs
import discord
from discord.ext import commands, tasks

GUILD = os.getenv("GUILD")
CHANNEL = os.getenv("CHANNEL")


class Astropix(commands.Cog):
    """A Discord Cog to handle scraping and sending the NASA picture of the day.

    ...

    Attributes
    ----------
    bot: commands.Bot
        The bot object from the main cog runner

    Methods
    -------
    scrape_and_send()
        Scrapes and sends the NASA picture of the day.
    schedule_send()
        Coordinates the timing of the scrape_and_send() function.
    """

    def __init__(self, bot: commands.Bot):
        """Initializes the cog.

        Parameters
        -----------
        bot: commands.Bot
            The bot object from the main cog runner.
        guild: discord.Guild
            The guild as specified in the config file.
        channel: disord.Channel
            The channel as specified in the config file.
        schedule_send: discord.ext.task
            Used to start the Discord task scheduler
        """

        self.bot = bot
        self.guild = bot.get_guild(int(GUILD))
        self.channel = self.guild.get_channel(int(CHANNEL))
        self.schedule_send.start()

    async def scrape_and_send(self):
        """Scrapes and sends the astronomy picture of the day.

        Utilizes beautiful soup to scrape the page for the image and the description,
        then sends all of it together in a message to the server. It's a rather simple
        function but it gets the job done.
        """

        # Grabs the page with a static link (literally has not changed since the 90s)
        html_page = urllib.request.urlopen("https://apod.nasa.gov/apod/astropix.html")
        soup = bs.BeautifulSoup(html_page)
        images = []
        alt = ""

        # Finds the images on the page
        for img in soup.findAll("img", alt=True):
            images.append(img.get("src"))
            alt = img.get("alt")

        # Creates an aiohttp session and grabs the image and makes a discord.File object in order to send it properly, then crashes itself
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
        """Handles the looping of the scrape_and_send() function."""
        await self.scrape_and_send()


async def setup(bot: commands.Bot):
    """Sets up the cog

    Parameters
    -----------
    bot: commands.Bot
       The main cog runners commands.Bot object
    """
    await bot.add_cog(Astropix(bot))
    print("Astropix: I'm loaded 😎")
