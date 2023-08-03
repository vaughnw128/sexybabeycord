"""
    Test_astropix

    Tests the astronomy picture of the day cog

    Made with love and care by Vaughn Woerpel
"""

# external
import pytest

from bot import constants

# project modules
from bot.exts.astropix import scrape_astropix
from bot.utils import file_helper


@pytest.mark.asyncio
async def test_scrape_image(bot):
    """Test grabbing astronomy picture of the day"""

    fname, _ = await scrape_astropix()
    assert fname == f"{constants.Bot.file_cache}astropix.jpg"
    file_helper.remove(fname)
