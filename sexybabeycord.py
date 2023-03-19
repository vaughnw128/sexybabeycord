import discord
from discord.ext import commands
from discord import app_commands
from config import token
import os

intents = discord.Intents.all()

client = commands.Bot(command_prefix='$', intents=intents)

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
    print('Bot online!')
    await load_extensions()

client.run(token)