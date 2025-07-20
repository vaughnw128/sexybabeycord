"""Fixlink

Automatically corrects twitter, instagram, and tiktok link
to their safe-embedded counterparts (vx, dd)

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
from typing import Optional

# external
import discord
from discord.ext import commands

# project modules
log = logging.getLogger("fixlink")

link_regex = (
    r"https:\/\/((www.|)tiktok|(www.|)twitter|(www.|)instagram|(www.|)x).com([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
)


class FixLink(commands.Cog):
    """Fixlink class to handle the... fixing of links"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize fixlink"""
        self.bot = bot
        log.info("FixLink cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Fix links on message if they match the regex"""
        if message.author.bot:
            return
            
        new_message = await fixlink(message)
        if new_message is not None:
            log.debug(f"Fixed link from {message.author}: {message.content[:50]}...")
            try:
                await message.delete()
                await message.channel.send(new_message)
                log.info(f"Successfully fixed and reposted link from {message.author}")
            except Exception as e:
                log.error(f"Failed to fix link from {message.author}: {e}")


async def fixlink(message: discord.Message) -> Optional[str]:
    """Helper method for fixing links"""
    # Searches for the link regex from the message
    link = re.search(
        link_regex,
        message.content,
    )

    # If the regex matched, create the new link
    if link is not None:
        original_link = link.group(0)
        link_parts = re.split(r"(https:\/\/www.|https:\/\/)", original_link)
        link_parts = list(filter(lambda x: len(x) > 0, link_parts))
        
        if "instagram" in link_parts[1]:
            fixed_link = link_parts[0] + "dd" + link_parts[1]
        elif "x.com" in link_parts[1]:
            fixed_link = link_parts[0] + link_parts[1].replace("x.com", "vxtwitter.com")
        else:
            fixed_link = link_parts[0] + "vx" + link_parts[1]
            
        log.debug(f"Fixed link: {original_link} -> {fixed_link}")
        new_message = f"{message.author.mention} {re.sub(link_regex, '', message.content)}\n{fixed_link}"
        return new_message
    else:
        return None


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(FixLink(bot))
        log.info("FixLink cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load FixLink cog: {e}")
        raise
