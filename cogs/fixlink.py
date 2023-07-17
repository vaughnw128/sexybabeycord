# fixlink.py
# Simple cog to fix twitter, tiktok, and instagram links so they can embed properly into discord
from discord.ext import tasks, commands
import re

class FixLink(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        
        link = re.search(r"https:\/\/((www.|)tiktok|(www.|)twitter|(www.|)instagram).com([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])", message.content)
        
        if link is not None:
            link = link.group(0)
            link = re.split(r"(https:\/\/www.|https:\/\/)", link)
            link = list(filter(lambda x: len(x) > 0, link))
            if "instagram" in link[1]:
                link = link[0] + "dd" + link[1]
            else:
                link = link[0] + "vx" + link[1]
            await message.delete()
            await message.channel.send(f"{message.author.mention} I fixed that one up for you, buddy!\n{link}")

async def setup(bot: commands.Bot):
  """ Sets up the cog

     Parameters
     -----------
     bot: commands.Bot
        The main cog runners commands.Bot object
  """
  await bot.add_cog(FixLink(bot))
  print("fixlink: I'm loaded : 3")