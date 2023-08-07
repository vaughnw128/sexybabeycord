"""
    MoodMeter

    Allows users to set their mood using a command
    and dropdown menus

    Made with love and care by Vaughn Woerpel
"""

import datetime
import json

# built-in
import logging
import time

# external
import discord
from discord import app_commands
from discord.ext import commands

# project
from bot import constants

log = logging.getLogger("moodmeter")


class SelectNumber(discord.ui.Select):
    def __init__(self):
        options = []
        for i in range(0, 10):
            options.append(
                discord.SelectOption(
                    label=i, emoji=constants.MoodMeter.number_emojis[i]
                )
            )
        super().__init__(
            placeholder="Select an option", max_values=1, min_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.number = self.values[0]
        await interaction.response.defer()


class SelectLetter(discord.ui.Select):
    def __init__(self):
        options = []
        for i in range(0, 10):
            options.append(
                discord.SelectOption(
                    label=chr(i + 65), emoji=constants.MoodMeter.letter_emojis[i]
                )
            )
        super().__init__(
            placeholder="Select an option", max_values=1, min_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.letter = self.values[0]
        await interaction.response.defer()


class MoodView(discord.ui.View):
    def __init__(self, *, timeout=180):
        self.letter = "N"
        self.number = "N"

        super().__init__(timeout=timeout)
        self.add_item(SelectLetter())
        self.add_item(SelectNumber())

    @discord.ui.button(label="Go!", style=discord.ButtonStyle.green, row=2)
    async def go_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            f"Your mood is {self.letter}{self.number}"
        )

        timestamp = round(time.mktime(interaction.created_at.timetuple()))

        mood = {
            timestamp: {
                "user": interaction.user.id,
                "letter": self.letter,
                "number": self.number,
            }
        }

        with open("bot/resources/moodmeter.json", "w") as jsonFile:
            json.dump(mood, jsonFile, indent=4)

    async def on_timeout(self, interaction: discord.Interaction):
        interaction.message.edit(
            "MoodMeter has timed out. Please rerun the command if you wish to input your mood."
        )


class MoodMeter(commands.Cog):
    """MoodMeter class to handle all your happy and sad needs"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the MoodMeter class"""
        self.bot = bot

    @app_commands.command(name="mood")
    async def mood(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            file=discord.File("bot/resources/MoodMeter.png"),
            view=MoodView(),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(MoodMeter(bot))
    log.info("Loaded")
