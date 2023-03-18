# statcat.py - A discord daily stat tracking bot

import discord
from discord import app_commands
from discord.ext import tasks
import schedule
from datetime import datetime
from tzlocal import get_localzone
from config import token, guild, channel

MY_GUILD = discord.Object(id=int(guild))

class DailyStats():

    # Initializes the daily stats object with the date and time for the day
    def __init__(self):
        return
    
    # Creates and formats the embed for the daily stats
    def create_embed():
        return

    # Clears the daily stats and returns a new object, but saves that day's stats to a backup file
    def clear_stats():
        return

    # Gets stats for a specific day or a date/time range
    def stat_history():
        return
    
    # Updates the stats when called
    def update_stats():
        return

    

# My discord bot client with all of the setuphook stuff so that the webserver doesn't bork itself
class MyClient(discord.Client):

    # Define stat send times
    est = get_localzone()
    times = [
        datetime.time(hour=00, minute=00, tzinfo=est, time=)
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)
        self.send_stats.start()

    # Makes a setuphook for syncinhg commands
    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    # Says it's ready and gets the channel and guild
    async def on_ready(self):
        print('Bot online!')
        print(guild)
        self.guild = self.get_guild(int(guild))
        self.channel = self.guild.get_channel(int(channel))
        print(f"Guild: {self.guild}")
        print(f"Channel: {self.channel}")

    async def on_message(self, message):
        await update_stats(message)
    
    # Stat send command scheduled

    @tasks.loop(times=times)
    def send_stats(self):
        print("ibo")

        
#Define Client
client = MyClient(intents=discord.Intents.default())

@client.tree.command()
async def stats(interaction: discord.Interaction):
    await interaction.response.send_message("stats_placeholder")


# Runs the bot
client.run(token)