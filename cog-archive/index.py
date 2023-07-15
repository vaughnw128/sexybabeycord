import discord, logging, json
from discord.ext import commands, tasks
from discord import app_commands
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import datetime
from typing import Literal, Optional
import re

uri = ""

# Create a new client and connect to the server
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
collection = mongo_client['sexybabeycord']['messages']

class DateTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, date: str) -> Optional[datetime.date]:
        redate = re.compile("^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$")
        if redate.match(date):
            if "-" in date:
                return datetime.datetime.strptime(date, "%m-%d-%Y").date.isoformat()
            elif "/" in date:
                return datetime.datetime.strptime(date, "%m/%d/%Y").date.isoformat()
            else:
                return datetime.datetime.strptime(date, "%m.%d.%Y").date.isoformat()
        return None

class MsgIndexer(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="index")
    @app_commands.rename(date1="start-date")
    @app_commands.rename(date2="end-date")
    async def index(
        self, 
        interaction: discord.Interaction,
        date1: Optional[app_commands.Transform[datetime.datetime, DateTransformer]]="All", 
        date2: Optional[app_commands.Transform[datetime.datetime, DateTransformer]]="All"
    ) -> None:
        
        await interaction.response.send_message("Indexing messages...", ephemeral=True)
        
        print(date1)
        print(date2)

        messages = []
        for channel in interaction.guild.channels:
            if type(channel) is discord.TextChannel: 
                messages += [message async for message in channel.history(limit=None, after=date1, before=date2, oldest_first=True)]
        
        count = 0
        for count, message in enumerate(messages):
            message = {
                "_id" : message.id,
                "timestamp" : message.created_at,
                "channel" : message.channel.id,
                "author" : message.author.id,
                "content" : message.content,
                "num_attachments" : len(message.attachments),
                "gif" : (lambda a: True in a)([x in message.content for x in ("https://tenor.com/view", "https://giphy.com/gifs", ".gif")]),
                "mentions" : [x.id for x in message.mentions]
            }
            messages[count] = message

        try:
            collection.insert_many(messages, ordered=False)
        except pymongo.errors.BulkWriteError as e:
            count -= 1

        print(f"Inserted {count} entries in the collection")
    
    @app_commands.command(name="search")
    async def search(
        self, 
        interaction : discord.Interaction, 
        search: Optional[str] = None, 
        author: Optional[str] = None,
        search_option: Optional[Literal["normal", "regex"]] = "normal",
        gif: Optional[bool] = None,
        attachment: Optional[bool] = None,
        date1: Optional[app_commands.Transform[datetime.date, DateTransformer]]=None, 
        date2: Optional[app_commands.Transform[datetime.date, DateTransformer]]=None
        ):

        print(date1)
        print(date2)

        query = {}
        if search is not None: 
            if search_option == "regex":
                search = search.replace("\\","\\")
                print(search)
                searchquery = {"$regex" : search, "$options" : "i"}
                print(searchquery)
            else:
                searchquery = {"$regex" : f"\\b{search}\\b", "$options" : "i"}
            query["content"] = searchquery

        if author is not None: 
            if author[0] == "!":
                query["author"] = {"$not" : int(author[3:len(author)-1])}
            else:
                query["author"] = int(author[2:len(author)-1])
        
        if gif is not None: query["gif"] = gif
        if attachment is not None: 
            if attachment:
                query["attachment"] = {"$gt" : 0}
            else:
                query["attachment"] = {"$eq" : 0}
        if date1 or date2:
            if date1 and date2: query["date"] = {"timestamp" : {"$lte" : date2, "$gte" : date1}}
            elif date1: query["date"] = {"timestamp" : {"$gte" : date1}}
            elif date2: query["date"] = {"timestamp" : {"$lte" : date2}}

        
        await interaction.response.defer(ephemeral=True)
        found = collection.find(query)
        
        str_format = {
            "content": f"Search term: {search}\n",
            "search_option": f"Search option: {search_option}\n",
            "author": f"Author: {author}\n",
            "gif": f"Has gif: {gif}\n",
            "attachment": f"Has attachment: {attachment}",
            "date": f"Dates: {date1} to {date2}"
        }

        resp = "# Search Results\n\n"
        resp += f"Found {len(list(found))} messages\n"
        for key in query.keys():
            resp += str_format[key]

        await interaction.followup.send(resp)
        
    # @tasks.loop(time=time(hour = 16))
    # async def schedule_send(self):
    #     """ Handles the looping of the scrape_and_send() function. """
    #     await self.scrape_and_send()
        


async def setup(bot: commands.Bot):
    """ Sets up the cog

        Parameters
        -----------
        bot: commands.Bot
        The main cog runners commands.Bot object
    """

    # Adds the cog and reports that it's loaded
    await bot.add_cog(MsgIndexer(bot))
    print("MsgIndexer: I'm loaded 8=====D")