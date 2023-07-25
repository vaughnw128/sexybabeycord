
from discord.ext import commands
import pkgutil
import types
import inspect
import importlib
from bot import exts
import discord
import bot
from bot import constants

class Sexybabeycord(commands.Bot):
    """ Discord bot sublass for Sexybabeycord """

    def __init__(self, *args, **kwargs):
        """ Initialize the bot class """
        super().__init__(*args, **kwargs)

    async def sync_app_commands(self) -> None:
        """ Sync the command tree to the guild """
        await self.tree.sync()
        await self.tree.sync(guild=discord.Object(constants.Guild.id))
    
    async def load_extensions(self, module: types.ModuleType) -> None:
        """ Load all cogs """
        for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}."):
            if module_info.ispkg:
                imported = importlib.import_module(module_info.name)
                if not inspect.isfunction(getattr(imported, "setup", None)):
                    # If it lacks a setup function, it's not an extension.
                    continue
            await self.load_extension(module_info.name)

    async def setup_hook(self) -> None:
        await self.load_extensions(exts)
        await self.sync_app_commands()