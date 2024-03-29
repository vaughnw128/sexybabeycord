"""MoodMeter

Allows users to set their mood using a command
and dropdown menus

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
from io import BytesIO

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
        for i in range(10):
            options.append(discord.SelectOption(label=i, emoji=constants.MoodMeter.number_emojis[i]))
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.number = self.values[0]
        await interaction.response.defer()


class SelectLetter(discord.ui.Select):
    def __init__(self):
        options = []
        for i in range(10):
            options.append(discord.SelectOption(label=chr(i + 65), emoji=constants.MoodMeter.letter_emojis[i]))
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

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
    async def go_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Your mood is {self.letter}{self.number}")
        file = await drop_pin(self.letter + self.number, interaction.user)
        await interaction.channel.send(file=discord.File(fp=file, filename="moodmeter.png"))

    async def on_timeout(self, interaction: discord.Interaction):
        interaction.message.edit("MoodMeter has timed out. Please rerun the command if you wish to input your mood.")


class MoodMeter(commands.Cog):
    """MoodMeter class to handle all your happy and sad needs"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the MoodMeter class"""
        self.bot = bot

    @app_commands.command(name="mood", description="Generate a moodmeter for yourself! Meow!")
    async def mood(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            file=discord.File("bot/resources/MoodMeter.png"),
            view=MoodView(),
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Allows users to do moods from a message regex"""
        match = re.search(r"MOOD\s([A-J][0-9])\b", message.content.upper())

        if match is not None:
            mood_match = match.group(1)
            await message.reply(f"Your mood is {mood_match}")
            file = await drop_pin(mood_match, message.author)
            await message.channel.send(file=discord.File(fp=file, filename="moodmeter.png"))


async def drop_pin(mood: str, user: discord.User) -> BytesIO:
    x = constants.MoodMeter.location[mood[0]]
    y = constants.MoodMeter.location[mood[1]]

    avatar, ext = await file_helper.grab_file_bytes(user.avatar.url)

    with Image(filename=constants.MoodMeter.image) as image:
        with Image(file=avatar) as avatar:
            avatar.resize(50, 50)
            avatar.crop()
            image.composite(avatar, left=(x - (avatar.width // 2)), top=(y - (avatar.height // 2)))
            buf = BytesIO()
            image.save(file=buf)
            buf.seek(0)
            return buf


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(MoodMeter(bot))
    log.info("Loaded")
