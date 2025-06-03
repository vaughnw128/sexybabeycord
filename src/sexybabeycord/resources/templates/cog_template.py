"""Discord bot cog template

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging

# external
import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("template")


class CogTemplate(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the command context menu"""
        self.bot = bot

        # Command tree menu
        self.template_menu = app_commands.ContextMenu(name="template", callback=self.template_ctx)
        self.bot.tree.add_command(self.template_menu)

        # Database stuff
        self.db = self.bot.database

        # Starting scheduled jobs
        self.check_reminders.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Template for on_message"""
        await message.channel.send("Template")

    @app_commands.command(name="template")
    async def mood(self, interaction: discord.Interaction) -> None:
        """Template for slash commands"""
        await interaction.response.defer()

        await interaction.response.send_message("Template")

    async def template_ctx(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Right click menu command template"""
        await interaction.response.defer()

        await interaction.response.send_message("Template")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(CogTemplate(bot))
    log.info("Loaded")
