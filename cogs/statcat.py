""" Statcat (A Sexybabeycord Cog)

    This cog is an isolated portion of the main Sexybabeycord bot.
    It's primary function is to generate statistics based on cached messages
    from a discord server, then display those stats to users in an easy-to-read manner.

    Made with love and care by Vaughn Woerpel
"""

from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
import datetime
import json
import os
import time
from typing import Optional
import re

date_choices = []

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
        
        dates = [datetime.datetime(2019,11,14,0,0,0)+datetime.timedelta(days=x) for x in range((datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(days=1)-datetime.datetime(2019,11,14,0,0,0)).days)]
        for date in dates:
            # print(type(date))
            date_choices.append(app_commands.Choice(name=str(date.date()), value=str(date.date())))

    @app_commands.command(name="loadmessages")
    async def loadmessages(self, interaction: discord.Interaction, startdate: Optional[str]=None, enddate: Optional[str]=None):
        """ Loads messages into json files based on user-supplied dates
        
            Takes in either a date range, a date, or nothing (current date), and then caches all messages
            from that date range to the /data directory. It skips over dates that have already been done,
            and saves specific attributes of the message for further analysis.

            ...

            Parameters
            -----------
            startdate: Optional[str]
                The start date of the date range
            enddate: Optional[str]
                The end date of the date range
        """
        
        dates = date_handler(startdate, enddate)

        #Lets the user know what's going on
        await interaction.response.send_message(f"Processing... This may take a moment!")
        
        # Starts a timer and a message count for later output
        start = time.time()
        message_count = 0
        
        # Loops along the date range and runs the message history
        for date in dates:
            # If the file exists already, skip over that date. This saves time for future operations if the date doesn't need to be indexed
            if os.path.exists(f"data/messages-{date.date()}.json"):
                continue
            messages = []

            # Gets the message history for all text channels on the specified date
            for channel in interaction.guild.channels:
                if type(channel) is discord.TextChannel: 
                    messages += [message async for message in channel.history(limit=None, after=date, before=date+datetime.timedelta(days=1), oldest_first=True)]
            message_count += len(messages)

            # Translates the messages to a dict, then puts it into a json file for that date
            messages_to_json(messages, date)

        # Ends the timer then outputs the results to the user
        end = time.time()
        await interaction.channel.send(f"Cached {message_count} from {startdate} to {enddate} in {round(end-start, 2)} seconds.")

    @app_commands.command(name="statcat")
    @app_commands.rename(date1="start-date")
    @app_commands.rename(date2="end-date")
    async def statcat(
        self, 
        interaction: 
        discord.Interaction, 
        option: Literal['word', 'user'], 
        search: str, 
        date1: Optional[app_commands.Transform[datetime.datetime , DateTransformer]]=datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), 
        date2: Optional[app_commands.Transform[datetime.datetime, DateTransformer]]=datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
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


        if date1 is None or date2 is None:
            await interaction.response.send_message(content="It seems you've entered the date in the wrong format. Try MM-dd-YYYY or MM/dd/YYYY", ephemeral=True)
        else:
            await interaction.response.send_message(content="Wait just a meowment :3", ephemeral=True)

        
        dates = [date1+datetime.timedelta(days=x) for x in range((date2-date1).days)]
        dates.append(date2)

        
        print(date1)
        print(date2)
        print(dates)



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

def date_handler(startdate, enddate):
    # Changes the specified dates to datetime
    startdate = to_datetime(startdate)
    enddate = to_datetime(enddate)

    # Horrendous if statement that decides how the dates should be arranged for the upcoming message history query
    if startdate is None and enddate is None:
        startdate = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        enddate = datetime.datetime.today()
    elif startdate is not None and enddate is None:
        enddate = startdate
    elif startdate is None and enddate is not None:
        startdate = enddate

    #Creates a list of dates between the inputs provided. If it's empty, set it to the startdate. If not, add the end date to cap it off
    
    if len(dates) == 0:
        dates.append(startdate)
    else:
        dates.append(enddate)
    
    return dates


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