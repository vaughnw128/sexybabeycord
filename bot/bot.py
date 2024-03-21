"""
File_helper

Custom bot class to implement some useful stuff

Made with love and care by Vaughn Woerpel
"""

# built-in
import importlib
import inspect
import logging
import pkgutil
import traceback
import types

# external
import discord
from discord.ext import commands
from discord import app_commands

# project modules
from bot import constants, exts

log = logging.getLogger("bot")


class Sexybabeycord(commands.Bot):
    """Discord bot subclass for Sexybabeycord"""

    def __init__(self, database, *args, **kwargs):
        """Initialize the bot class"""
        self.database = database
        super().__init__(*args, **kwargs)

    async def sync_app_commands(self) -> None:
        """Sync the command tree to the guild"""

        await self.tree.sync()
        await self.tree.sync(guild=discord.Object(constants.Guild.id))

        logging.info("Command tree synced")

    async def load_extensions(self, module: types.ModuleType) -> None:
        """Load all cogs by walking the packages in exts."""

        logging.info("Loading extensions")
        for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}."):
            if module_info.ispkg:
                imported = importlib.import_module(module_info.name)
                if not inspect.isfunction(getattr(imported, "setup", None)):
                    continue
            await self.load_extension(module_info.name)
        logging.info("Extensions loaded")

    async def setup_hook(self) -> None:
        """Replacing default setup_hook to run on startup"""

        await self.load_extensions(exts)
        await self.sync_app_commands()
        self.tree.on_error = self.global_app_command_error
        log.info("Started")

    async def global_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Handles app command errors"""
        if isinstance(error, discord.app_commands.CommandInvokeError):
            log.error(traceback.format_exc())
            await interaction.followup.send("An unexpected error has occurred.")
        elif isinstance(error, app_commands.AppCommandError):
            await interaction.followup.send(error)
        else:
            log.error(traceback.format_exc())

    async def on_error(self, event: str, *args, **kwargs) -> None:
        """Handles exts errors"""

        message = args[0]
        log.warning("ERROR CAUGHT")
        log.warning(f"Event: {event}")
        log.warning(f"Message: {message}")
        log.warning(traceback.format_exc())
