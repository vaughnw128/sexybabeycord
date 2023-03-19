import discord
from discord.ext import commands
from typing import Literal, Optional
from discord import app_commands
from config import token, guild
import os
from discord.ext.commands import Greedy, Context
import logging

intents = discord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents)

@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
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

# Load all of the cogs
async def load_extensions():
    # await client.load_extension("cogs.statcat")
    # await client.load_extension("cogs.astropix")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")

@client.event
async def on_ready():
    print("Sexybabeycord: Now I'm all spooled up!")
    await load_extensions()

client.run(token)