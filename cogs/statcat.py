""" Statcat (A Sexybabeycord Cog)

    This cog is an isolated portion of the main Sexybabeycord bot.
    It's primary function is to generate statistics based on cached messages
    from a discord server, then display those stats to users in an easy-to-read manner.

    Made with love and care by Vaughn Woerpel
"""

from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import json
import os
import time
from typing import Optional
import re
from config import guild
from dateutil import tz

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/New_York')

class DateTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, date: str) -> Optional[datetime.datetime]:
        redate = re.compile("^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$")
        if redate.match(date):
            if "-" in date:
                return datetime.datetime.strptime(date, "%m-%d-%Y")
            elif "/" in date:
                return datetime.datetime.strptime(date, "%m/%d/%Y")
            else:
                return datetime.datetime.strptime(date, "%m.%d.%Y")
        return None

class Statcat(commands.Cog):
    """ A Discord Cog to handle all of the statistic-generating functionalities of the Sexybabeycord bot.

        ---

        Attributes
        ----------
        bot: `commands.Bot`
            The bot object from the main cog runner

        Methods
        -------
        loadmessages(`interaction`, `startdate`, `enddate`)
            Loads messages within the date range to json data files.
    """

    def __init__(self, bot: commands.Bot):
        """ Initializes the cog.

            Parameters
            -----------
            bot: commands.Bot
                The bot object from the main cog runner.
        """
        self.bot = bot
        self.guild = self.bot.get_guild(int(guild))
        self.cache_previous_day.start()

    @tasks.loop(time=datetime.time(hour=0, minute=1))
    async def cache_previous_day(self):
        date = (datetime.datetime.today()-datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # If the file exists already, remove the file and redo it
        if os.path.exists(f"data/messages-{date.date()}.json"):
            os.remove(f"data/messages-{date.date()}.json")
        
        messages = []
        # Gets the message history for all text channels on the specified date
        for channel in self.guild.channels:
            if type(channel) is discord.TextChannel: 
                messages += [message async for message in channel.history(limit=None, after=date, before=date+datetime.timedelta(days=1), oldest_first=True)]

        # Translates the messages to a dict, then puts it into a json file for that date
        messages_to_json(messages, date)

    @app_commands.command(name="statcat")
    @app_commands.rename(date1="start-date")
    @app_commands.rename(date2="end-date")
    async def statcat(
        self, 
        interaction: 
        discord.Interaction, 
        option: Literal['message', 'word', 'image', 'gif', 'mention'], 
        search: Optional[str]=None,
        user: Optional[str]=None, 
        date1: Optional[app_commands.Transform[datetime.datetime, DateTransformer]]="All", 
        date2: Optional[app_commands.Transform[datetime.datetime, DateTransformer]]="All"
    ) -> None:
        """ Generates stats from cached messages
        
            Takes in either a date range, a date, or nothing (current date), and then generates stats
            based on cached messages in the /data directory.

            ---

            Parameters
            -----------
            option: Literal['word', 'user']
                The option for what to generate stats for
            search: str
                What to search for based on the option command
            date1: Optional[str]
                The start date of the date range
            date2: Optional[str]
                The end date of the date range
        """

        # Tells the user to wait a sec
        await interaction.response.defer(ephemeral=True)

        # Gets the dates
        start = time.time()
        dates = await date_handler(interaction, date1, date2)
        if dates is None:
            return
        end = time.time()
        print(f"date_handler: {end-start}")

        start = time.time()
        messages = await load_messages(interaction, dates)
        end = time.time()
        print(f"load_messages: {end-start}")

        start = time.time()
        stats = generate_stats(search, messages, user)
        end = time.time()
        print(f"generate_stats: {end-start}")

        await interaction.followup.send(stats)
        
def generate_stats(search, messages, user):
    stats = {
        "messages": 0,
        "words": 0,
        "images": 0,
        "gifs": 0,
        "mentions": {},
        "authors": {},
        "dates": {}
    }

    for date in messages:
        for message in messages[date]:
            inc = 1
            if search is not None:
                wc = len(re.findall(r"\b"+re.escape(search)+r"\b", message["content"].lower()))
                stats["words"] += wc
                if wc == 0:
                    inc = 0

            stats["messages"] += inc
            stats["images"] += message["num_attachments"]*inc
            stats["gifs"] += (lambda x : inc if x else 0)(message["gif"])
            # if inc == 1 and message["gif"]:
            #     print(message["content"])

            for mention in message["mentions"]:
                if mention not in stats["mentions"]:
                    stats["mentions"][mention] = inc
                else:
                    stats["mentions"][mention] += inc
            
            if message["author"] not in stats["authors"]:
                stats["authors"][message["author"]] = inc
            else:
                stats["authors"][message["author"]] += inc

            if date.date() not in stats["dates"]:
                stats["dates"][date.date()] = inc
            else:
                stats["dates"][date.date()] += inc

    stats["mentions"] = sorted(stats["mentions"].items(), key=lambda x:x[1], reverse=True)[0]
    stats["authors"] = sorted(stats["authors"].items(), key=lambda x:x[1], reverse=True)[0]
    stats["dates"] = sorted(stats["dates"].items(), key=lambda x:x[1], reverse=True)[0]

    return stats


def utc_to_est(date):
    global from_zone
    global to_zone
    utc = date.replace(tzinfo=from_zone)
    est_date = str(utc.astimezone(to_zone).date())
    return est_date

async def date_handler(interaction: discord.Interaction, date1, date2):
    if date1 is None or date2 is None:
        await interaction.response.send_message(content="It seems you've entered the date in the wrong format. Try MM-dd-YYYY or MM/dd/YYYY", ephemeral=True)
        return None
    elif date1 == "All" and date2 == "All":
        dates = [datetime.datetime(2019,11,14,0,0,0)+datetime.timedelta(days=x) for x in range((datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(days=1)-datetime.datetime(2019,11,14,0,0,0)).days)]
    elif date1 == "All":
        dates = [date2]
    elif date2 == "All":
        dates = [date1]
    else:
        dates = [date1+datetime.timedelta(days=x) for x in range((date2+datetime.timedelta(days=1)-date1).days)]
    if len(dates) == 0:
        await interaction.response.send_message(content="You flipped your start-date and end-date! Fix that, why don't you!?", ephemeral=True)
        return None
    return dates

async def load_messages(interaction, dates):
    message_dict = {}

    # TODO: potentially implement this? it adds a lot of time
    # today = (datetime.datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
        
    # # Remove current day so that it can be replaced
    # if os.path.exists(f"data/messages-{today.date()}.json"):
    #     os.remove(f"data/messages-{today.date()}.json")
    for date in dates:
        if not os.path.exists(f"data/messages-{date.date()}.json"):
            # Gets the message history for all text channels on the specified date
            messages = []
            for channel in interaction.guild.channels:
                if type(channel) is discord.TextChannel: 
                    messages += [message async for message in channel.history(limit=None, after=date, before=date+datetime.timedelta(days=1), oldest_first=True)]

            # Translates the messages to a dict, then puts it into a json file for that date
            messages_to_json(messages, date)
        
        with open(f"data/messages-{date.date()}.json", 'r') as messages_json:
            temp_dict = json.load(messages_json)
            message_dict[date] = temp_dict["messages"]
    return message_dict

def messages_to_json(messages, date):
    """ Formats messages into dictionary/json format and writes them to a file.

        Takes the input from the loadmessages() command, then outputs them into a file labeled with the provided date.

        ...

        Parameters
        -----------
        messages: list of str
            List of messages to format and write to file.
        date: datetime.datetime
            Datetime.datetime object of the current date index of the calling for loop.
    """

    # Initializes and empty dict and then loops through messages
    dict_to_json = {"messages": []}
    for message in messages:
        # Special formatting for the message dict, altering things like whether the message has a gif or not, and who the message mentions
        message_dict = {
            "message_id" : message.id,
            "timestamp" : str(message.created_at),
            "channel" : message.channel.id,
            "author" : message.author.id,
            "content" : message.content,
            "num_attachments" : len(message.attachments),
            "gif" : (lambda a: True in a)([x in message.content for x in ("https://tenor.com/view", "https://giphy.com/gifs", ".gif")]),
            "mentions" : [x.id for x in message.mentions]
        }
        dict_to_json["messages"].append(message_dict)

    # If the dict is empty simply return and do not write to a file
    if len(dict_to_json["messages"]) == 0:
        return
    
    # Checks if the file exists, and if it does not, dumps the data to the file
    if not os.path.exists(f"data/messages-{date.date()}.json"):
        with open(f"data/messages-{date.date()}.json", 'w') as messages_json:
            print(f"data/messages-{date.date()}.json")
            json.dump(dict_to_json, messages_json, indent=4)
    else:
        return

async def setup(bot: commands.Bot):
  """ Sets up the cog

     Parameters
     -----------
     bot: commands.Bot
        The main cog runners commands.Bot object
  """

  # Adds the cog and reports that it's loaded
  await bot.add_cog(Statcat(bot))
  print("Statcat: I'm loaded 😼")