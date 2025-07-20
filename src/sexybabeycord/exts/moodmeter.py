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
from sexybabeycord import constants
from sexybabeycord.utils import file_helper

log = logging.getLogger("moodmeter")


class SelectNumber(discord.ui.Select):
    def __init__(self) -> None:
        options = []
        for i in range(10):
            options.append(discord.SelectOption(label=str(i), emoji=constants.MoodMeter.number_emojis[i]))
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        self.view.number = self.values[0]
        await interaction.response.defer()


class SelectLetter(discord.ui.Select):
    def __init__(self) -> None:
        options = []
        for i in range(10):
            options.append(discord.SelectOption(label=chr(i + 65), emoji=constants.MoodMeter.letter_emojis[i]))
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        self.view.letter = self.values[0]
        await interaction.response.defer()


class MoodView(discord.ui.View):
    def __init__(self, *, timeout: int = 180) -> None:
        self.letter: str = "N"
        self.number: str = "N"

        super().__init__(timeout=timeout)
        self.add_item(SelectLetter())
        self.add_item(SelectNumber())

    @discord.ui.button(label="Go!", style=discord.ButtonStyle.green, row=2)
    async def go_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        log.debug(f"Mood selection from {interaction.user}: {self.letter}{self.number}")
        await interaction.response.send_message(f"Your mood is {self.letter}{self.number}")

        try:
            file = await drop_pin(self.letter + self.number, interaction.user)
            await interaction.channel.send(file=discord.File(fp=file, filename="moodmeter.png"))
            log.info(f"Successfully generated mood meter for user {interaction.user}")
        except Exception as e:
            log.error(f"Failed to generate mood meter for user {interaction.user}: {e}")
            await interaction.followup.send("Failed to generate mood meter", ephemeral=True)

    async def on_timeout(self, interaction: discord.Interaction) -> None:
        log.debug(f"MoodMeter timed out for user {interaction.user}")
        await interaction.message.edit(
            content="MoodMeter has timed out. Please rerun the command if you wish to input your mood."
        )


class MoodMeter(commands.Cog):
    """MoodMeter class to handle all your happy and sad needs"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the MoodMeter class"""
        self.bot = bot
        log.info("MoodMeter cog initialized")

    @app_commands.command(name="mood", description="Generate a moodmeter for yourself! Meow!")
    async def mood(self, interaction: discord.Interaction) -> None:
        log.debug(f"Mood command from {interaction.user}")
        try:
            await interaction.response.send_message(
                file=discord.File("bot/resources/MoodMeter.png"),
                view=MoodView(),
                ephemeral=True,
            )
            log.info(f"Successfully sent mood command response to {interaction.user}")
        except Exception as e:
            log.error(f"Failed to send mood command response to {interaction.user}: {e}")
            raise

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Allows users to do moods from a message regex"""
        match = re.search(r"MOOD\s([A-J][0-9])\b", message.content.upper())

        if match is not None:
            mood_match = match.group(1)
            log.debug(f"Mood regex match from {message.author}: {mood_match}")

            try:
                await message.reply(f"Your mood is {mood_match}")
                file = await drop_pin(mood_match, message.author)
                await message.channel.send(file=discord.File(fp=file, filename="moodmeter.png"))
                log.info(f"Successfully processed mood regex for user {message.author}")
            except Exception as e:
                log.error(f"Failed to process mood regex for user {message.author}: {e}")
                await message.reply("Failed to generate mood meter")


async def drop_pin(mood: str, user: discord.User) -> BytesIO:
    """Generate a mood meter image with user's avatar at the specified mood position"""
    log.debug(f"Generating mood meter for user {user} with mood {mood}")

    try:
        x = constants.MoodMeter.location[mood[0]]
        y = constants.MoodMeter.location[mood[1]]

        avatar, ext = await file_helper.grab_file_bytes(user.avatar.url)
        log.debug(f"Retrieved avatar for user {user}")

        with Image(filename=constants.MoodMeter.image) as image:
            with Image(file=avatar) as avatar:
                avatar.resize(50, 50)
                avatar.crop()
                image.composite(avatar, left=(x - (avatar.width // 2)), top=(y - (avatar.height // 2)))
                buf = BytesIO()
                image.save(file=buf)
                buf.seek(0)
                log.debug(f"Successfully generated mood meter image for user {user}")
                return buf

    except Exception as e:
        log.error(f"Failed to generate mood meter for user {user}: {e}")
        raise


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(MoodMeter(bot))
        log.info("MoodMeter cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load MoodMeter cog: {e}")
        raise
