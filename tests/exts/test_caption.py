""" 
    Test_caption

    Tests the captioning cog

    Made with love and care by Vaughn Woerpel
"""

# external
import discord.ext.test as dpytest
import pytest

# project modules
from bot.exts.caption import caption_helper


@pytest.mark.asyncio
async def test_no_caption(bot):
    """Test grabbing astronomy picture of the day"""

    original_message = await dpytest.message("https://tenor.com/view/sexybabeys-sexybabeyscord-sexybabeycord-vaughn-vaughncord-gif-18421747")
    message = await original_message.reply("")
    assert await caption_helper(message) == "Message doesn't start with caption"

@pytest.mark.asyncio
async def test_no_original(bot):
    """Test grabbing astronomy picture of the day"""

    message = await dpytest.message("caption what was I supposed to be doing again?")
    assert await caption_helper(message) == "Message is not a reply"

# @pytest.mark.asyncio
# async def test_no_caption_text(bot):
#     """Test grabbing astronomy picture of the day"""

#     original_message = await dpytest.message("https://tenor.com/view/sexybabeys-sexybabeyscord-sexybabeycord-vaughn-vaughncord-gif-18421747")
#     message = await original_message.reply("caption")
#     log.error(message.reference.message_id)
#     assert await caption_helper(message) == None

# @pytest.mark.asyncio
# async def test_no_file(bot):
#     """Test grabbing astronomy picture of the day"""

#     original_message = await dpytest.message("I'm not a file!")
#     message = await original_message.reply("caption this isn't a file")
#     assert await caption_helper(message) == None

# @pytest.mark.asyncio
# async def test_wrong_filetype(bot):
#     """Test grabbing astronomy picture of the day"""

#     original_message = await dpytest.message("https://download.havecamerawilltravel.com/sample-images/webp/webp-example.webp")
#     message = await original_message.reply("caption this is a webp file")
#     assert await caption_helper(message) == None

# @pytest.mark.asyncio
# async def test_correct(bot):
#     """Test grabbing astronomy picture of the day"""

#     original_message = await dpytest.message("https://tenor.com/view/sexybabeys-sexybabeyscord-sexybabeycord-vaughn-vaughncord-gif-18421747")
#     message = await original_message.reply("caption testing")
#     fname = await caption_helper(message)
#     # assert await caption_helper(message) == None
#     assert 1 == None
