import discord
from discord import app_commands
from discord.ext import commands, tasks
import pytz
import datetime
import json
import os







""" TODO: CREATE A SCRIPT THAT GRABS ALL DISCORD HISTORY BETWEEN DATES AND THEN CACHES IT"""

class Statcat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.batch = []
        self.save_batch.start()

    @commands.Cog.listener("on_message")
    async def get_message(self, message):
        msg_dict = {
            "message_id" : message.id,
            "timestamp" : str(message.created_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/New_York"))),
            "channel" : message.channel.id,
            "author" : message.author.id,
            "content" : message.content,
            "num_attachments" : len(message.attachments),
            "gif" : (lambda a: True in a)([x in message.content for x in ("https://tenor.com/view", "https://giphy.com/gifs", ".gif")]),
            "mentions" : [x.id for x in message.mentions]
        }

        self.batch.append(msg_dict)

    @tasks.loop(minutes=5.0)
    #@tasks.loop(time=datetime.time(hour = 23, minute = 59, second = 59, microsecond=59))
    async def save_batch(self):
        
        if not os.path.exists(f"data/messages-{datetime.date.today()}.json"):
            with open(f"data/messages-{datetime.date.today()}.json", 'w') as messages_json:
                filler = {"messages" : []}
                json.dump(filler, messages_json, indent=4)

        with open(f"data/messages-{datetime.date.today()}.json", "r") as messages_json:
            day_data = json.load(messages_json)
            combined_batch = day_data['messages'] + self.batch
            messages_json.close()

        dump = {"messages": combined_batch}

        with open(f"data/messages-{datetime.date.today()}.json", "w") as messages_json:
            json.dump(dump, messages_json, indent=4)
            messages_json.close()
        self.batch = []
    
    @app_commands.command(name="scrapemessages")
    async def scrape_messages(self, interaction: discord.Interaction):
        messages = [message async for message in interaction.channel.history(limit=None)]
        print(messages)
    
    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")


async def setup(bot: commands.Bot):
  await bot.add_cog(Statcat(bot))
  print("Cog - Statcat Loaded!")