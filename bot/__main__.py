"""
__main__

Initializes the discord client object and runs the async main function

Made with love and care by Vaughn Woerpel
"""

# built-in
import asyncio

# external
import discord
from pymongo import MongoClient
from pymongo.errors import ConfigurationError

# project modules
from bot import constants
from bot.bot import Sexybabeycord


async def main() -> None:
    """Define bot parameters and initialize the client object"""

    intents = discord.Intents.all()

    try:
        mongo_client = MongoClient(constants.Database.connection_uri)
        database = mongo_client.get_database(constants.Database.database)
    except ConfigurationError:
        database = None

    client = Sexybabeycord(
        database=database,
        intents=intents,
        command_prefix=constants.Bot.prefix,
    )

    await client.start(constants.Bot.token)


if __name__ == "__main__":
    """Run the bot"""

    asyncio.run(main())
