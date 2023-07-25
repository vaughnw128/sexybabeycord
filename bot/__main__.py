from bot.bot import Sexybabeycord
from bot import constants
import asyncio
import discord

async def main() -> None:
    intents = discord.Intents.all()
    client = Sexybabeycord(intents=intents, command_prefix=constants.Bot.prefix)
    await client.start(constants.Bot.token)

if __name__ == "__main__":
    asyncio.run(main())
