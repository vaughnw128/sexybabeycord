"""
    Remind

    Lets users set reminders for the future

    Made with love and care by Vaughn Woerpel
"""

import datetime

# built-in
import logging
import re
import time
from typing import Literal

# external
import discord
from discord import app_commands
from discord.ext import commands
from wand.image import Image

# project
from bot import constants

log = logging.getLogger("remind")


class DateTransformer(app_commands.Transformer):
    async def transform(
        self, interaction: discord.Interaction, date: str
    ) -> datetime.date | None:
        redate = re.compile(
            r"^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$"
        )
        if redate.match(date):
            if "-" in date:
                return datetime.datetime.strptime(date, "%m-%d-%Y").date.isoformat()
            elif "/" in date:
                return datetime.datetime.strptime(date, "%m/%d/%Y").date.isoformat()
            else:
                return datetime.datetime.strptime(date, "%m.%d.%Y").date.isoformat()
        return None


class Remind(commands.Cog):
    """Remind class"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the Remind class"""
        self.bot = bot
        self.db = self.bot.database

    @app_commands.command(name="remind", description="Set a reminder for later!")
    @app_commands.describe(
        reason="reminder reason",
        inon="reminded in a time or on a date",
        duration="in how long",
        unit="what unit",
        later="what date",
    )
    async def remind(
        self,
        interaction: discord.Interaction,
        reason: str,
        inon: Literal["in", "on"],
        duration: int | None,
        unit: Literal["minutes", "hours", "days"] | None,
        later: app_commands.Transform[datetime.datetime, DateTransformer] | None,
    ) -> None:
        await interaction.response.defer()

        now = datetime.datetime.now()
        if inon == "in":
            later = now + datetime.timedelta(**{unit: duration})
            print(later)
        else:
            later = later.replace(hour=12, minute=0, second=0)
            print(later)

        reminder = {
            "timestamp": now.replace(microsecond=0),
            "user": interaction.user.id,
            "guild": interaction.guild.id,
            "reason": reason,
            "later": later.replace(microsecond=0),
        }

        print(self.db.Reminders)
        self.db.Reminders.insert_one(reminder)

        await interaction.followup.send("Sent to DB!")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Remind(bot))
    log.info("Loaded")
