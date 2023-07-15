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
# from dateutil import tz
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator, MaxNLocator)
import matplotlib.dates as mdates
import math

# from_zone = tz.gettz('UTC')
# to_zone = tz.gettz('America/New_York')

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
        interaction: discord.Interaction, 
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

        messages = await load_messages(interaction, dates)
        
        stats = generate_stats(search, messages, user, option)
        
        end = time.time()
        runtime = round(end-start, 2)
        embed = generate_embed(self, interaction, stats, search, user, dates, runtime, option)
        await interaction.channel.send(embed=embed)
        await interaction.followup.send("Done!")
    
    @app_commands.command(name="statgraph")
    @app_commands.rename(date1="start-date")
    @app_commands.rename(date2="end-date")
    async def statgraph(
        self, 
        interaction: discord.Interaction, 
        option: Literal['message', 'word', 'image', 'gif', 'mention'], 
        search: Optional[str]=None,
        user: Optional[str]=None, 
        date1: Optional[app_commands.Transform[datetime.datetime, DateTransformer]]="All", 
        date2: Optional[app_commands.Transform[datetime.datetime, DateTransformer]]="All"
    ) -> None:
        # Tells the user to wait a sec
        await interaction.response.defer(ephemeral=True)

        # Gets the dates
        start = time.time()
        dates = await date_handler(interaction, date1, date2)
        if dates is None:
            return

        messages = await load_messages(interaction, dates)
        stats = generate_stats(search, messages, user, option)

        sorted_dates = sorted(dict(stats["dates"]).items(), key=lambda x: x[0])
        date_list = [[elem1, elem2] for elem1, elem2 in sorted_dates]
        
        stat_dates = []
        if len(date_list) > 28:
            for i,date in enumerate(date_list):
                if i % 7 == 0:
                    stat_dates.append(date)
                else:
                    stat_dates[i//7][1] += date[1] 
        else:
            stat_dates = date_list

        plt.close('all')

        if len(date_list) > 28:
            dtFmt = mdates.DateFormatter('%Y-%b') # define the formatting
            plt.gca().xaxis.set_major_formatter(dtFmt) 
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        else:
            dtFmt = mdates.DateFormatter('%Y-%b-%d') # define the formatting
            plt.gca().xaxis.set_major_formatter(dtFmt) 
        
        plt.xticks(rotation=45, fontsize='x-small')
        
        ticklist = [x[1] for x in stat_dates]
        ticklist = range(math.floor(min(ticklist)), math.ceil(max(ticklist))+1)
        plt.yticks(ticklist)
        plt.locator_params(axis='y', nbins=10)
        plt.plot(*zip(*stat_dates))

        title = f"{option}s between {dates[0].date()} and {dates[len(dates)-1].date()}"
        if search is not None:
            title += f"\nSearch: {search}"
        if user is not None:
            title += f", User: {self.bot.get_user(int(user[2:len(user)-1]))}"
        plt.title(title)
        plt.xlabel("Dates")
        plt.savefig('stats.png')

        await interaction.followup.send("Done!")
        await interaction.channel.send(file=discord.File("stats.png"))

def generate_embed(self, interaction, stats, search, user, dates, runtime, option):
    embed=discord.Embed(title="Statistics", description=f"Message statistics for {interaction.guild} between {dates[0].date()} and {dates[len(dates)-1].date()}", color=0x6de0bd)
    embed.add_field(name="Option", value=f"`{option}`", inline=False)
    if user is not None:
        embed.add_field(name="Searched User", value=f"`{self.bot.get_user(int(user[2:len(user)-1]))}`", inline=False)
    if option != "gif" and option != "image":
        embed.add_field(name="Message Count", value=f"`{stats['message_count']}`", inline=False)
    if search is not None:
        embed.add_field(name="Searched String", value=f"{search}", inline=False)
        embed.add_field(name="Occurance Count", value=f"`{stats['word_count']}`", inline=False)
        option = search
    if option != "gif":
        embed.add_field(name="Image Count", value=f"`{stats['image_count']}`", inline=False)
    if option != "image":
        embed.add_field(name="Gif Count", value=f"`{stats['gif_count']}`", inline=False)
    if user is None:
        embed.add_field(name="Author", value=f"User `{self.bot.get_user(stats['authors'][0][0])}` sent `{stats['authors'][0][1]}` {option}s", inline=False)
    embed.add_field(name="Date", value=f"`{stats['dates'][0][1]}` {option}s were sent on `{stats['dates'][0][0]}`", inline=False)
    # embed.add_field(name="Mentions", value=stats["mentions"][0], inline=False)
    embed.set_footer(text=f"Generated in {runtime} seconds.")
    return embed

def generate_stats(search, messages, user, option):
    stats = {
        "message_count": 0,
        "word_count": 0,
        "image_count": 0,
        "gif_count": 0,
        "mentions": {},
        "authors": {},
        "dates": {},
        "gifs": {}
    }

    for date in messages:
        for message in messages[date]:
            inc, wc, gc, ic = 1, 1, 1, 1

            if user is not None:
                if str(message["author"]) != user[2:len(user)-1]:
                    inc = 0

            if search is not None:
                wc = len(re.findall(r"\b"+re.escape(search.lower())+r"\b", message["content"].lower()))
                stats["word_count"] += wc*inc
                if wc == 0:
                    inc = 0

            stats["message_count"] += inc
            stats["image_count"] += message["num_attachments"]*inc

            if option == "gif" and not message["gif"]:
                inc = 0
            
            if option == "image" and message["num_attachments"] == 0:
                inc = 0

            if message["gif"]:
                giflink = re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)", message["content"])
                if giflink is not None:
                    stats["gif_count"] += inc
                    giflink = giflink.group(0)

                    if giflink not in stats["gifs"]:
                        stats["gifs"][giflink] = inc
                    else:
                        stats["gifs"][giflink] += inc

            for mention in message["mentions"]:
                if mention not in stats["mentions"]:
                    stats["mentions"][mention] = inc
                else:
                    stats["mentions"][mention] += inc
            
            if message["author"] not in stats["authors"]:
                stats["authors"][message["author"]] = inc*wc
            else:
                stats["authors"][message["author"]] += inc*wc

            if date.date() not in stats["dates"]:
                stats["dates"][date.date()] = inc*wc
            else:
                stats["dates"][date.date()] += inc*wc

    stats["mentions"] = sorted(stats["mentions"].items(), key=lambda x:x[1], reverse=True)
    stats["authors"] = sorted(stats["authors"].items(), key=lambda x:x[1], reverse=True)
    stats["dates"] = sorted(stats["dates"].items(), key=lambda x:x[1], reverse=True)
    stats["gifs"] = sorted(stats["gifs"].items(), key=lambda x:x[1], reverse=True)

    return stats


async def date_handler(interaction: discord.Interaction, date1, date2):
    if date1 is None or date2 is None:
        await interaction.followup.send(content="It seems you've entered the date in the wrong format. Try MM-dd-YYYY or MM/dd/YYYY", ephemeral=True)
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
        await interaction.followup.send(content="You flipped your start-date and end-date! Fix that, why don't you!?", ephemeral=True)
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