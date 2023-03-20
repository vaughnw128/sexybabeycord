import discord
from discord.ext import commands
from typing import Literal, Optional
from config import token
import os
from discord.ext.commands import Greedy, Context

# Defines the bot intents and the client
intents = discord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents)

@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    r""" Loads messages into json files based on user-supplied dates
        
        Syncing to the command tree is important as this is how the guild populates itself with the discord app_commands.

        ...

        Parameters
        -----------
        ctx: Context
            Command context object
        guilds: Optional[discord.Object]
            List of guilds
        spec: Optional[Literal["~", "*", "^"]
            Optional specification for what the sync command should do: sync the tree, copy the tree, or clear the tree.
        """

    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

async def load_cogs():
    """ Loads all of the cogs in the /cogs directory.
    
        Cogs allow for a more streamlined process of managing a large bot.
    """
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

@client.event
async def on_ready():
    """ Discord client event for when the bot is ready
    
        Runs as soon as the bot starts
    """
    print("Sexybabeycord: Now I'm all spooled up!")
    await load_cogs()

client.run(token)