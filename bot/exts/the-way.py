"""
    The Way

    Gets a daoist verse, and sends it

    Made with love and care by Vaughn Woerpel
"""

# built-in
import io
import json
import logging
import random
import urllib
from datetime import time

# external
import aiohttp
import bs4 as bs
import discord
from discord import app_commands
from discord.ext import commands, tasks

# project modules
from bot import constants
from bot.utils import file_helper

log = logging.getLogger("the-way")


class TheWay(commands.Cog):
    """A Discord Cog to handle sending a daily daoist message."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the cog."""

        with open("./bot/resources/the-way.json") as f:
            data = json.load(f)

        self.verses = []
        for collection in data["collections"]:
            for book in data["collections"][collection]:
                for chapter_title in data["collections"][collection][book]:
                    for chapter in chapter_title.values():
                        for verse in chapter:
                            self.verses.append(dict(verse))

        self.bot = bot
        self.schedule_send.start()

    @tasks.loop(time=time(hour=16))
    async def schedule_send(self) -> None:
        """Handles the looping of the scrape_and_send() function."""

        channel = await self.bot.fetch_channel(constants.Channels.yachts)
        verse = dict(random.choice(self.verses))
        await channel.send(f"```{verse['chinese']}\n\n{verse['english']}```")

    @app_commands.command(name="verse")
    async def verse(self, interaction: discord.Interaction):
        await interaction.response.defer()
        verse = dict(random.choice(self.verses))
        await interaction.followup.send(
            f"```{verse['chinese']}\n\n{verse['english']}```"
        )


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(TheWay(bot))
    log.info("Loaded")
