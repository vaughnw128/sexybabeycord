"""
Test_gabonganized

Tests the distort cog

Made with love and care by Vaughn Woerpel
"""

# external
import discord.ext.test as dpytest
import pytest

# project modules
from bot.exts.speechtotext import speech_to_text_helper


@pytest.mark.asyncio
async def test_no_file(bot):
    """Test gabonganizing without a file"""

    message = await dpytest.message("Hello, world!")
    assert await speech_to_text_helper(message) == "Message had no file"


@pytest.mark.asyncio
async def test_no_voice_message(bot):
    """Test gabonganizing an image with no faces"""

    message = await dpytest.message(
        content="",
        attachments=["https://download.havecamerawilltravel.com/sample-images/webp/webp-example.webp"],
    )
    assert await speech_to_text_helper(message) == "Not a voice message"


# @pytest.mark.asyncio
# async def test_hello(bot):
#     """Test gabonganizing an image with no faces"""

#     message = await dpytest.message(
#         content="",
#         attachments=[
#             "https://cdn.discordapp.com/attachments/644752766736138241/1136727329310261329/voice-message.ogg"
#         ],
#     )
#     assert await speech_to_text_helper(message) == "hello sexy baby cord"
