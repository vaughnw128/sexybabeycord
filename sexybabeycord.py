import asyncio
import discord
import importlib
import inspect
import pkgutil
from discord.ext import commands
import types

from bot import exts

class Sexybabeycord(commands.Bot):

    async def load_extensions(self, module: types.ModuleType):
        modules = set()

        for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}."):
            if module_info.ispkg:
                imported = importlib.import_module(module_info.name)
                if not inspect.isfunction(getattr(imported, "setup", None)):
                    # If it lacks a setup function, it's not an extension.
                    continue
            modules.add(module_info.name)
    
        for ext in modules:
            self.load_extension(ext)

    async def setup_hook(self) -> None:
        """Default async initialisation method for discord.py."""
        await super().setup_hook()
        await self.load_extensions(exts)