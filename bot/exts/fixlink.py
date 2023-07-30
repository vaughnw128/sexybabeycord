""" 
    Fixlink

    Automatically corrects twitter, instagram, and tiktok link
    to their safe-embedded counterparts (vx, dd)

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re

# external
import discord
from discord.ext import commands

# project modules
log = logging.getLogger("fixlink")


class FixLink(commands.Cog):
    """Fixlink class to handle the... fixing of links"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize fixlink"""

        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Fix links on message if they match the regex"""

        link_regex = r"https:\/\/((www.|)tiktok|(www.|)twitter|(www.|)instagram).com([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"

        link = re.search(
            link_regex,
            message.content,
        )

        if link is not None:
            link = link.group(0)
            link = re.split(r"(https:\/\/www.|https:\/\/)", link)
            link = list(filter(lambda x: len(x) > 0, link))
            if "instagram" in link[1]:
                link = link[0] + "dd" + link[1]
            else:
                link = link[0] + "vx" + link[1]
            await message.delete()
            await message.channel.send(
                f"{message.author.mention} {re.sub(link_regex, '', message.content)}\n{link}"
            )


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(FixLink(bot))
    log.info("Loaded")
