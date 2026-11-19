"""Nickname Ledger

Posts to a ledger channel whenever someone changes their nickname

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging

# external
import discord
from discord.ext import commands

# project
from sexybabeycord import constants

log = logging.getLogger("nickname_ledger")


class NicknameLedger(commands.Cog):
    """Logs nickname changes to the ledger channel"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the NicknameLedger cog"""
        self.bot = bot
        log.info("NicknameLedger cog initialized")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        """Post to the ledger channel when a member changes their nickname"""
        if before.nick == after.nick:
            return

        username = after.name
        old_nick = before.nick or before.name
        new_nick = after.nick or after.name

        log.debug(f"Nickname change from {before}: {old_nick!r} -> {new_nick!r}")

        try:
            channel = self.bot.get_channel(constants.Channels.ledger)
            if channel is None:
                log.error("Ledger channel not found")
                return

            embed = discord.Embed(
                description=f"{username} changed their nickname from {old_nick} to {new_nick}",
                color=discord.Color.blurple(),
            )
            await channel.send(embed=embed)
            log.info(f"Logged nickname change for {after}")
        except Exception as e:
            log.error(f"Failed to log nickname change for {after}: {e}")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(NicknameLedger(bot))
        log.info("NicknameLedger cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load NicknameLedger cog: {e}")
        raise
