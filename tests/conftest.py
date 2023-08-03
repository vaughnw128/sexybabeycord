"""
    Conftest

    Sets up everything for bot testing to occur

    Made with love and care by Vaughn Woerpel
"""

import glob
import os

import discord
import discord.ext.test as dpytest
import pytest_asyncio

from bot import constants
from bot.bot import Sexybabeycord
from bot.utils import file_helper


@pytest_asyncio.fixture
async def bot():
    """Initializes a bot instance for the testing functions to use"""
    intents = discord.Intents.all()
    client = Sexybabeycord(intents=intents, command_prefix=constants.Bot.prefix)

    await client._async_setup_hook()  # setup the loop
    await file_helper.setup()

    dpytest.configure(client)

    yield client

    # Teardown
    await dpytest.empty_queue()


def pytest_sessionfinish(session, exitstatus):
    """Code to execute after all tests."""

    # dat files are created when using attachements
    print("\n-------------------------\nClean dpytest_*.dat files")
    fileList = glob.glob("./dpytest_*.dat")
    for filePath in fileList:
        try:
            os.remove(filePath)
        except Exception:
            print("Error while deleting file : ", filePath)
