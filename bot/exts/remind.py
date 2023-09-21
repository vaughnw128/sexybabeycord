"""
    Remind

    Lets users set reminders for the future

    Made with love and care by Vaughn Woerpel
"""


import datetime

# built-in
import logging
import os
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

os.environ["TZ"] = "US/Eastern"
time.tzset()


class DeleteReminderView(discord.ui.View):
    def __init__(self, db, document, *, timeout=180):
        super().__init__(timeout=timeout)
        self.db = db
        self.document = document

    @discord.ui.button(label="Confirm Deletion", style=discord.ButtonStyle.red, row=1)
    async def delete_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        if interaction.user.id == self.document["user"]:
            self.db.Reminders.delete_one(filter=self.document)

            await interaction.message.edit(
                content="Reminder deleted.", embed=None, view=None
            )
            button.disabled = True


class ReminderView(discord.ui.View):
    def __init__(self, embeds, *, timeout=180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.loc = 0

    @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
    async def left_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        try:
            if self.loc != 0:
                self.loc -= 1
            else:
                self.loc = len(self.embeds) - 1
            await interaction.message.edit(embed=self.embeds[self.loc])
        except Exception:
            log.error("Button error")

    @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
    async def right_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        try:
            if self.loc != len(self.embeds) - 1:
                self.loc += 1
            else:
                self.loc = 0
            await interaction.message.edit(embed=self.embeds[self.loc])
        except Exception:
            log.error("Button error")

    async def on_timeout(self, interaction: discord.Interaction):
        interaction.message.edit("Reminder message has timed out.")


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
                    hour=12, second=0, microsecond=0
                )
            elif "/" in date:
                return datetime.datetime.strptime(date, "%m/%d/%Y").replace(
                    hour=12, second=0, microsecond=0
                )
            else:
                return datetime.datetime.strptime(date, "%m.%d.%Y").replace(
                    hour=12, second=0, microsecond=0
                )
        return None


class Remind(commands.Cog):
    """Remind class"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the Remind class"""
        self.bot = bot
        self.db = self.bot.database
        self.check_reminders.start()

    @tasks.loop(seconds=15)
    async def check_reminders(self) -> None:
        """Handles the looping of the checking reminders"""

        cursor = self.db.Reminders.find({})
        for document in cursor:
            if document["later"] < datetime.datetime.now():
                embed = discord.Embed(title="DING! Get reminded!!", color=0xFB0DA8)

                embed.add_field(
                    name="", value=f"**Reason:** `{document['reason']}`", inline=False
                )
                embed.add_field(
                    name="",
                    value=f"**Time:** `{document['later']}`",
                    inline=False,
                )
                embed.add_field(
                    name="", value=f"\n\n{document['message_url']}", inline=False
                )

                channel = await self.bot.fetch_channel(document["channel"])
                await channel.send(embed=embed, content=f"<@{document['user']}>")

                self.db.Reminders.delete_one(filter=document)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Checks to see if someone wants to be reminded"""

        # Searches for the link regex from the message
        is_reminder = re.search(
            "remind me",
            message.content.lower(),
        )

        # If the regex matched send a reminder to use remind
        if is_reminder is not None:
            await message.reply(
                "Hey buddy! You know there's a feature for that... Why don't you try `/remind`?"
            )

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
        elif later == None:
            interaction.followup.send(
                "Wrong date format! Please enter in MM-DD-YYYY format."
            )
            return

        embed = discord.Embed(
            title="Reminder Generated!",
            description=f"@{interaction.user.display_name}",
            color=0xFB0DA8,
        )
        embed.add_field(name="", value=f"**Reason:** `{reason}`", inline=False)
        embed.add_field(
            name="",
            value=f"**Time:** `{later.replace(microsecond=0)}`",
            inline=False,
        )
        message = await interaction.followup.send(embed=embed)

        reminder = {
            "timestamp": now.replace(microsecond=0),
            "user": interaction.user.id,
            "channel": interaction.channel.id,
            "guild": interaction.guild.id,
            "reason": reason,
            "later": later.replace(microsecond=0),
            "message_url": message.jump_url,
        }

        self.db.Reminders.insert_one(reminder)

    @app_commands.command(name="reminders", description="Get a list of your reminders")
    async def reminders(
        self,
        interaction: discord.Interaction,
    ) -> None:
        await interaction.response.defer()

        cursor = self.db.Reminders.find({"user": interaction.user.id})
        cursor_length = len(list(cursor))

        cursor = self.db.Reminders.find({"user": interaction.user.id})
        embeds = []

        count = 1
        for document in cursor:
            embed = discord.Embed(title="Reminder", color=0xFB0DA8)
            embed.add_field(
                name="", value=f"**Reason:** `{document['reason']}`", inline=False
            )
            embed.add_field(
                name="",
                value=f"**Time:** `{document['later']}`",
                inline=False,
            )
            embed.add_field(
                name="", value=f"\n\n{document['message_url']}", inline=False
            )
            embed.set_footer(text=f"{count}/{cursor_length}")
            count += 1
            embeds.append(embed)

        if len(embeds) > 1:
            await interaction.followup.send(embed=embeds[0], view=ReminderView(embeds))
        elif len(embeds) == 0:
            await interaction.followup.send("No reminders found!")
        else:
            await interaction.followup.send(embed=embeds[0])

    @app_commands.command(
        name="delreminder", description="Delete a reminder that matches a reason"
    )
    @app_commands.describe(reason="reminder reason")
    async def delreminder(self, interaction: discord.Interaction, reason: str) -> None:
        await interaction.response.defer()

        cursor = self.db.Reminders.find({"user": interaction.user.id, "reason": reason})

        docs = []
        for document in cursor:
            docs.append(document)

        if len(docs) == 0:
            await interaction.followup.send("No reminders found.")
            return

        document = docs[0]
        embed = discord.Embed(title="Reminder", color=0xFB0DA8)
        embed.add_field(
            name="", value=f"**Reason:** `{document['reason']}`", inline=False
        )
        embed.add_field(
            name="",
            value=f"**Time:** `{document['later']}`",
            inline=False,
        )
        embed.add_field(name="", value=f"\n\n{document['message_url']}", inline=False)

        await interaction.followup.send(
            content="Delete this reminder?",
            embed=embed,
            view=DeleteReminderView(self.db, document),
        )


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Remind(bot))
    log.info("Loaded")
