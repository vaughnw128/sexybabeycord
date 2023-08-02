""" 
    Test_file_helper

    Tests bot/utils/file_helper

    Made with love and care by Vaughn Woerpel
"""

# external
import discord.ext.test as dpytest
import pytest

# project modules
from bot import constants
from bot.utils import file_helper

@pytest.mark.asyncio
async def test_grab_file_simple_url(bot):
    """Test broken mime type url"""
    
    message = await dpytest.message("https://images.pexels.com/photos/4587955/pexels-photo-4587955.jpeg?cs=srgb&dl=pexels-anna-shvets-4587955.jpg&fm=jpg")
    fname = file_helper.grab(message)
    assert fname == f"{constants.Bot.file_cache}pexels-photo-4587955.jpeg"
    file_helper.remove(fname)


@pytest.mark.asyncio
async def test_grab_file_broken_mime_url(bot):
    """Test broken mime type url"""
    
    message = await dpytest.message("https://images.unsplash.com/photo-1574144611937-0df059b5ef3e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZnVubnklMjBjYXR8ZW58MHx8MHx8fDA%3D&w=1000&q=80")
    fname = file_helper.grab(message)
    assert fname == f"{constants.Bot.file_cache}photo-1574144611937-0df059b5ef3e.jpeg"
    file_helper.remove(fname)


@pytest.mark.asyncio
async def test_grab_file_gif_url(bot):
    """Test gif url"""
    
    message = await dpytest.message("https://media.tenor.com/2roX3uxz_68AAAAM/cat-space.gif")
    fname = file_helper.grab(message)
    assert fname == f"{constants.Bot.file_cache}cat-space.gif"
    file_helper.remove(fname)


@pytest.mark.asyncio
async def test_grab_file_tenor_url(bot):
    """Test tenor url"""

    message = await dpytest.message("https://tenor.com/view/sexybabeys-sexybabeyscord-sexybabeycord-vaughn-vaughncord-gif-18421747")
    fname = file_helper.grab(message)
    assert fname == f"{constants.Bot.file_cache}sexybabeys-sexybabeyscord.gif"
    file_helper.remove(fname)


# @pytest.mark.asyncio
# async def test_grab_file_vxtwitter_url(bot):
#     """Test vxtwitter url"""

#     message = await dpytest.message("https://vxtwitter.com/JamesCageWhite/status/1686029940687310848")
#     log.error(message.embeds)
#     fname = file_helper.grab(message)
#     assert fname == f"{constants.Bot.file_cache}F2X7SLRWIAAon-6.jpg"


@pytest.mark.asyncio
async def test_grab_file_attachment_gif(bot):
    """Test attachment gif"""

    message = await dpytest.message(content="", attachments=["https://media.discordapp.net/attachments/644752766736138241/1136141577467723989/nyan.gif"])
    fname = file_helper.grab(message)
    assert fname == f"{constants.Bot.file_cache}nyan.gif"
    file_helper.remove(fname)


@pytest.mark.asyncio
async def test_grab_file_attachment_jpg(bot):
    """Test attachment jpg"""

    message = await dpytest.message(content="", attachments=["https://images-ext-2.discordapp.net/external/UYsSEFKavGjDMUVHnZF3B3odIp98mx1_vavpjda4rBM/https/pbs.twimg.com/media/F2X7SLRWIAAon-6.jpg?width=418&height=558"])
    fname = file_helper.grab(message)
    assert fname == f"{constants.Bot.file_cache}F2X7SLRWIAAon-6.jpg"
    file_helper.remove(fname)

