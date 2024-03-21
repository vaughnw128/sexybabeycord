"""Wrench

Allows for a few testing features

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging

# external
import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("wrench")


class Wrench(commands.Cog):
    """Test cog for debugging features"""

    def __init__(self, bot: commands.Bot):
        """Initializes class with context menu"""
        self.bot = bot
        self.message_json = app_commands.ContextMenu(name="View Message JSON", callback=self.message_json_menu)
        self.bot.tree.add_command(self.message_json)

    async def message_json_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.defer()

        response = f"=== Message ===\n\n{message!s}"

        if len(message.embeds) > 0:
            response += f"\n\n=== Embed ===\n\n{message.embeds[0].to_dict()!s}"

        await interaction.followup.send(content=f"```{response}```")


async def setup(bot: commands.Bot):
    """Sets up the cog"""
    # Adds the cog and reports that it's loaded
    await bot.add_cog(Wrench(bot))
    log.info("Loaded")
