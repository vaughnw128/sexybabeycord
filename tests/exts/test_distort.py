"""
    Test_distort

    Tests the distort cog

    Made with love and care by Vaughn Woerpel
"""

# external
import discord.ext.test as dpytest
import pytest

from bot import constants

# project modules
from bot.exts.distort import distort_helper
from bot.utils import file_helper


@pytest.mark.asyncio
async def test_no_file(bot):
    """Test distorting without a file"""

    message = await dpytest.message("Hello, world!")
    assert await distort_helper(message) == "Message had no file"


@pytest.mark.asyncio
async def test_wrong_filetype(bot):
    """Test distorting without a filetype"""

    message = await dpytest.message(
        "https://download.havecamerawilltravel.com/sample-images/webp/webp-example.webp"
    )
    assert await distort_helper(message) == "Invalid filetype"


@pytest.mark.asyncio
async def test_image(bot):
    """Test distorting an image"""

    message = await dpytest.message(
        "https://t3.ftcdn.net/jpg/01/20/68/68/360_F_120686889_nDaqiMH8I5AmT5B0hpuJ14ZasdrrgRAK.jpg"
    )
    assert (
        await distort_helper(message)
        == f"{constants.Bot.file_cache}360_F_120686889_nDaqiMH8I5AmT5B0hpuJ14ZasdrrgRAK.jpg"
    )
    file_helper.remove(
        f"{constants.Bot.file_cache}360_F_120686889_nDaqiMH8I5AmT5B0hpuJ14ZasdrrgRAK.jpg"
    )


@pytest.mark.asyncio
async def test_gif(bot):
    """Test distorting a gif"""

    message = await dpytest.message(
        "https://mir-s3-cdn-cf.behance.net/project_modules/hd/22550858835329.5a0b39c26d469.gif"
    )
    assert (
        await distort_helper(message)
        == f"{constants.Bot.file_cache}22550858835329.5a0b39c26d469.gif"
    )
    file_helper.remove(f"{constants.Bot.file_cache}22550858835329.5a0b39c26d469.gif")
