import discord
from discord.ext import tasks, commands
from config import guild, channel
import bs4 as bs
import aiohttp
import urllib
import io
from datetime import time

class Astropix(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = bot.get_guild(int(guild))
        self.channel = self.guild.get_channel(int(channel))
        self.schedule_send.start()
    
    # Scrapes then sends the astro pic
    async def scrape_and_send(self):
        html_page = urllib.request.urlopen("https://apod.nasa.gov/apod/astropix.html")
        soup = bs.BeautifulSoup(html_page)
        images = []
        alt=""
        for img in soup.findAll('img', alt=True):
            images.append(img.get('src'))
            alt = img.get('alt')
        
        # Creates an aiohttp session and grabs the image and makes a discord.File object in order to send it properly, then crashes itself
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://apod.nasa.gov/{images[0]}") as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await self.channel.send(content=f"Astronomy Picture of the Day!\n\n{alt}\n\nhttps://apod.nasa.gov/apod/astropix.html", file=discord.File(file, "astropic.jpg"))

    @tasks.loop(time=time(hour = 12))
    async def schedule_send(self):
        await self.scrape_and_send()

async def setup(bot: commands.Bot):
  await bot.add_cog(Astropix(bot))
  print("Astropix: I'm loaded 😎")