import discord
from discord.ext import tasks, commands
import syllables
import re
import cmudict

def lookup_word(word_s):
    return cmudict.dict().get(word_s)

def count_syllables(word_s):
    count = 0
    phones = lookup_word(word_s) # this returns a list of matching phonetic rep's
    if phones:                   # if the list isn't empty (the word was found)
        phones0 = phones[0]      #     process the first
        count = len([p for p in phones0 if p[-1].isdigit()]) # count the vowels
    return count

class Haiku(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        content = message.content.replace("\n", " ")
        regex = re.compile('[^a-zA-Z ]')
        content = regex.sub('', content)
        buildstring = ""
        num_syllables = 0
        for word in content.split():
            buildstring += f"{word} "
            num_syllables += syllables.estimate(word)
            if num_syllables == 5:
                buildstring += "\n"
            if num_syllables == 12:
                buildstring += "\n"

        if len(buildstring.split('\n')) > 2 and num_syllables == 17:
            await message.reply("Nice haiku!\n\n"+buildstring)

async def setup(bot: commands.Bot):
  """ Sets up the cog

     Parameters
     -----------
     bot: commands.Bot
        The main cog runners commands.Bot object
  """
  await bot.add_cog(Haiku(bot))
  print("Haiku: I'm loaded : 3")

