import discord
from discord import app_commands
from discord.ext import commands, tasks
import pytz
import datetime
import json
import os
from typing import Optional

class Statcat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.batch = []
        self.save_batch.start()

    @tasks.loop(minutes=5.0)
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
    
    @app_commands.command(name="loadmessages")
    async def loadmessages(self, interaction: discord.Interaction, startdate: str=None, enddate: str=None):
        r""" Loads messages into json files based on user-supplied dates
        
        Attributes
        -----------
        startdate: Optional[:class:`str`]
            The start date of the date range
        enddate: Optional[:class:`str`]
            The end date of the date range
        """
        
        startdate = to_datetime(startdate)
        enddate = to_datetime(enddate)

        if startdate is None and enddate is None:
            startdate = datetime.datetime.today()
            enddate = datetime.datetime.today()
        elif startdate is not None and enddate is None:
            enddate = startdate
        elif startdate is None and enddate is not None:
            startdate = enddate
        # else:
        #     enddate = enddate+datetime.timedelta(days=1)

        startdate = startdate-datetime.timedelta(days=1)
        
        dates = [startdate+datetime.timedelta(days=x) for x in range((enddate-startdate).days)]
        dates.append(dates[len(dates)-1]+datetime.timedelta(days=1))
        
        for date in dates:
            messages = []
            for channel in interaction.guild.channels:
                if type(channel) is discord.TextChannel: 
                    print(f"Channel: {channel.name}\nStartdate: {date}\nEnddate: {date+datetime.timedelta(days=1)}")
                    messages += [message async for message in channel.history(limit=None, after=date, before=date+datetime.timedelta(days=1), oldest_first=True)]
            messages_to_json(messages)
    
    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

def to_datetime(date) -> Optional[datetime.datetime]:
    """Formats the date string to a datetime object"""
    if date is not None:
        date = datetime.datetime.strptime(date, "%m-%d-%Y")

    return date

def messages_to_json(messages):
    for message in messages:
        message_dict = {
            "message_id" : message.id,
            "timestamp" : str(message.created_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/New_York"))),
            "channel" : message.channel.id,
            "author" : message.author.id,
            "content" : message.content,
            "num_attachments" : len(message.attachments),
            "gif" : (lambda a: True in a)([x in message.content for x in ("https://tenor.com/view", "https://giphy.com/gifs", ".gif")]),
            "mentions" : [x.id for x in message.mentions]
        }

        print(message_dict)

async def setup(bot: commands.Bot):
  await bot.add_cog(Statcat(bot))
  print("Statcat: I'm loaded 😼")