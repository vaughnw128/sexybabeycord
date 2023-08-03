""" 
    Test_gabonganized

    Tests the distort cog

    Made with love and care by Vaughn Woerpel
"""

# external
import discord.ext.test as dpytest
import pytest

# project modules
from bot.exts.gabonganized import gabonga_helper
from bot import constants
from bot.utils import file_helper

@pytest.mark.asyncio
async def test_no_file(bot):
    """Test gabonganizing without a file"""

    message = await dpytest.message("Hello, world!")
    assert await gabonga_helper(message) == "Message had no file"


@pytest.mark.asyncio
async def test_invalid_filetype(bot):
    """Test gabonganizing with wrong filetype"""

    message = await dpytest.message("https://download.havecamerawilltravel.com/sample-images/webp/webp-example.webp")
    assert await gabonga_helper(message) == "Invalid filetype"

@pytest.mark.asyncio
async def test_no_faces(bot):
    """Test gabonganizing an image with no faces"""

    message = await dpytest.message("https://images-ext-2.discordapp.net/external/8FCqAqtjOBQLZF80cEtw6L5J774L0hqNoL3uur49E68/https/pbs.twimg.com/media/F2kkiCFa0AEzxlL.jpg?width=502&height=669")
    assert await gabonga_helper(message) == "No faces in image"
    file_helper.remove(f"{constants.Bot.file_cache}F2kkiCFa0AEzxlL.jpg")

@pytest.mark.asyncio
async def test_image(bot):
    """Test gabonganizing an image"""

    message = await dpytest.message("https://images-ext-1.discordapp.net/external/WjnwUTwFktFOau3aa2ktj-qFFmK1WxqoNz-DbvNuCNk/%3Fimgs%3Dhttps%3A%2F%2Fpbs.twimg.com%2Fmedia%2FF2gCnMmbIAEOH0j.jpg%2Chttps%3A%2F%2Fpbs.twimg.com%2Fmedia%2FF2gCnMkacAA1oEs.jpg/https/vxtwitter.com/rendercombined.jpg?width=731&height=487")
    assert await gabonga_helper(message) == f"{constants.Bot.file_cache}rendercombined.jpg"
    file_helper.remove(f"{constants.Bot.file_cache}rendercombined.jpg")
