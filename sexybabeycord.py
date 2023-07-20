""" Sexybabeycord (A Sexybabeycord Production)

    The is the main runner file for the Sexybabeycord discord bot.
    The bot itself is a collection of multiple pieces, each with vastly
    different functionalities. There certainly will be more to come as our
    server never has enough bots (lie).

    What the hell is Sexybabeycord?: Sexybabeycord is the current iteration of the Discord server that I share
    with my close friends (we accidentally nuked the last one with homemade spambots). It's more of a 
    chaotic groupchat than a high-functioning Discord 'community,' as we all have Administrator 
    permissions, and we don't particularly care for rules. I love making bots for our server, and my
    friends seem to as well.

    The current components (cogs) of the bot are as follows:
        Astropix: Scrapes and sends the NASA picture of the day every day at noon.
        Statcat: Message statistics generator.
    
    Components that I plan on adding in the future:
        Distort: One of the oldest bots that I've written, but is now rusty and in disrepair. It needs to be revived!

    Made with love and care by Vaughn Woerpel
"""

import os
from typing import Literal, Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Defines the bot intents and the client
intents = discord.Intents.all()
client = commands.Bot(command_prefix="$", intents=intents)


@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: Context,
    guilds: Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    r"""Loads messages into json files based on user-supplied dates

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
    """Loads all of the cogs in the /cogs directory.

    Cogs allow for a more streamlined process of managing a large bot.
    """
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")


@client.event
async def on_ready():
    """Discord client event for when the bot is ready

    Runs as soon as the bot starts
    """
    print("Sexybabeycord: Now I'm all spooled up!")
    await load_cogs()


client.run(DISCORD_TOKEN)
