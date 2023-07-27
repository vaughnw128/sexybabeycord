""" Custom bot class to incorporate useful functions """

from discord.ext import commands
import pkgutil
import types
import inspect
import importlib
from bot import exts
import discord
from bot import constants
import logging

log = logging.getLogger("bot")

class Sexybabeycord(commands.Bot):
    """ Discord bot sublass for Sexybabeycord """

    def __init__(self, *args, **kwargs):
        """ Initialize the bot class """

        super().__init__(*args, **kwargs)

    async def sync_app_commands(self) -> None:
        """ Sync the command tree to the guild """

        await self.tree.sync()
        await self.tree.sync(guild=discord.Object(constants.Guild.id))
        logging.info("Command tree synced")
    
    async def load_extensions(self, module: types.ModuleType) -> None:
        """ Load all cogs by walking the packages in exts """

        logging.info("Loading extensions")
        for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}."):
            if module_info.ispkg:
                imported = importlib.import_module(module_info.name)
                if not inspect.isfunction(getattr(imported, "setup", None)):
                    continue
            await self.load_extension(module_info.name)
        logging.info("Extensions loaded")

    async def setup_hook(self) -> None:
        """ Replacing default setup_hook to run on startup """

        await self.load_extensions(exts)
        await self.sync_app_commands()
        log.info("Started")

    async def on_error(self, event: str, *args, **kwargs) -> None:
        """ Handles exts errors """
        
        print(f"Error in {event}")