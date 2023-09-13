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
from discord.ext import commands, tasks
from wand.image import Image

# project
from bot import constants

log = logging.getLogger("remind")


class DateTransformer(app_commands.Transformer):
    async def transform(
        self, interaction: discord.Interaction, date: str
    ) -> datetime.datetime | None:
        redate = re.compile(
            r"^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$"
        )
        if redate.match(date):
            if "-" in date:
                return datetime.datetime.strptime(date, "%m-%d-%Y").replace(
                    hour=17, second=0, microsecond=0
                )
            elif "/" in date:
                return datetime.datetime.strptime(date, "%m/%d/%Y").replace(
                    hour=17, second=0, microsecond=0
                )
            else:
                return datetime.datetime.strptime(date, "%m.%d.%Y").replace(
                    hour=17, second=0, microsecond=0
                )
        return None


class Remind(commands.Cog):
    """Remind class"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the Remind class"""
        self.bot = bot
        self.db = self.bot.database
        self.check_reminders.start()

    @tasks.loop(minutes=1)
    async def check_reminders(self) -> None:
        """Handles the looping of the checking reminders"""

        cursor = self.db.Reminders.find({})
        for document in cursor:
            print(document)
            # if document['later'] < datetime.datetime.now():

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

        reminder = {
            "timestamp": now.replace(microsecond=0),
            "user": interaction.user.id,
            "channel": interaction.channel.id,
            "guild": interaction.guild.id,
            "reason": reason,
            "later": later.replace(microsecond=0),
        }

        self.db.Reminders.insert_one(reminder)

        embed = discord.Embed(
            title="Reminder Generated!",
            description=f"@{interaction.user.display_name}",
            color=0xFB0DA8,
        )
        embed.add_field(name="", value=f"**Reason:** `{reason}`", inline=False)
        embed.add_field(name="", value=f"**Time:** `{later}`", inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Remind(bot))
    log.info("Loaded")
