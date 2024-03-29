"""
Soundboard cog

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
from pathlib import Path

# external
import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("soundboard")

class SelectSound(discord.ui.Select):
    def __init__(self):
        options = []
        for path in list(Path('./bot/resources/sounds').iterdir()):
            options.append(discord.SelectOption(label=path.name.replace(".mp3", ""), value=str(path)))
        super().__init__(placeholder="Select a sound", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.view.author_id:
            await interaction.message.edit(view=None, attachments=[discord.File(Path(self.values[0]), "sound.mp3")])


class SoundboardView(discord.ui.View):
    def __init__(self, author_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(SelectSound())
        self.sound = None
        self.author_id = author_id

    async def on_timeout(self, interaction: discord.Interaction):
        await interaction.message.edit("Soundboard has timed out!")
        await interaction.message.edit(view=None)

class Soundboard(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="sb")
    async def sb(self, interaction: discord.Interaction) -> None:
        """Creates a soundboard selection menu to select a sound with."""
        await interaction.response.send_message(view=SoundboardView(interaction.user.id))

async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Soundboard(bot))
    log.info("Loaded")
