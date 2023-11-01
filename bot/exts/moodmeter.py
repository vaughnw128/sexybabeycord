"""
    MoodMeter

    Allows users to set their mood using a command
    and dropdown menus

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
import time

# external
import discord
from discord import app_commands
from discord.ext import commands
from wand.image import Image

# project
from bot import constants
from bot.utils import file_helper

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
    def __init__(self, database, *, timeout=180):
        self.letter = "N"
        self.number = "N"
        self.db = database

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

        mood = {
            "timestamp": int(time.time()),
            "user": interaction.user.id,
            "guild": interaction.guild.id,
            "mood": self.letter + self.number,
        }

        if self.db is not None:
            self.db.MoodMeter.insert_one(mood)
        file = await drop_pin(self.letter + self.number, interaction.user)
        await interaction.channel.send(file=file)

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
            view=MoodView(database=self.bot.database),
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Allows users to do moods from a message regex"""

        match = re.search(r"MOOD\s([A-J][0-9])\b", message.content.upper())

        if match is not None:
            mood_match = match.group(1)

            await message.reply(f"Your mood is {mood_match}")

            mood = {
                "timestamp": int(time.time()),
                "user": message.author.id,
                "guild": message.guild.id,
                "mood": mood_match,
            }

            print(mood)

            self.bot.database.MoodMeter.insert_one(mood)
            file = await drop_pin(mood_match, message.author)
            await message.channel.send(file=file)


async def drop_pin(mood: str, user: discord.User) -> discord.File:
    x = constants.MoodMeter.location[mood[0]]
    y = constants.MoodMeter.location[mood[1]]

    avatar = file_helper.download_url(user.avatar.url)

    with Image(filename=constants.MoodMeter.image) as image:
        with Image(filename=avatar) as avatar:
            avatar.resize(50, 50)
            avatar.crop()
            image.composite(
                avatar, left=(x - (avatar.width // 2)), top=(y - (avatar.height // 2))
            )
            image.save(filename=f"{constants.Bot.file_cache}{user.name}_mood.png")

    return discord.File(f"{constants.Bot.file_cache}/{user.name}_mood.png")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(MoodMeter(bot))
    log.info("Loaded")
