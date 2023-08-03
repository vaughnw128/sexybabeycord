""" 
    Test_fixlink

    Tests the fixlink cog

    Made with love and care by Vaughn Woerpel
"""

# external
import discord.ext.test as dpytest
import pytest

# project modules
from bot.exts.fixlink import fixlink


@pytest.mark.asyncio
async def test_twitter(bot):
    """Test twitter -> vxtwitter"""

    message = await dpytest.message("https://twitter.com/JamesCageWhite/status/1686884877696892929")
    response = await fixlink(message)
    assert "https://vxtwitter.com/JamesCageWhite/status/1686884877696892929" in response

@pytest.mark.asyncio
async def test_tiktok(bot):
    """Test tiktok -> vxtiktok"""

    message = await dpytest.message("https://www.tiktok.com/@handsomejamescage/video/7143936716712217857")
    response = await fixlink(message)
    assert "https://www.vxtiktok.com/@handsomejamescage/video/7143936716712217857" in response

@pytest.mark.asyncio
async def test_instagram(bot):
    """Test instagram -> ddinstagram"""

    message = await dpytest.message("https://www.instagram.com/p/CvbgCyUrXxk/?hl=en")
    response = await fixlink(message)
    assert "https://www.ddinstagram.com/p/CvbgCyUrXxk/?hl=en" in response