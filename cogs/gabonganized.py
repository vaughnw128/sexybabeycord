# Gabonganized.py
# When someone sends a face pic, they get gabonganized. Simple as.
from discord.ext import commands
from wand.image import Image
import discord
import requests
import validators
import os
import urllib
import face_recognition


class Gabonga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Checks for the author being the bot
        if message.author == 873414777064542268:
            return
        
        # Grabs the file using reused distort bot code
        fname = await grab_file(message)
        if fname is None:
            return
        
        # Uses face rec to grab the face and get the location
        image = face_recognition.load_image_file(fname)
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 0:
            return

        # Tries to do multiple faces... might not work
        for face_location in face_locations:
            # Print the location of each face in this image
            top, right, bottom, left = face_location
            with Image(filename=fname) as face:
                with Image(filename="gabonga.png") as gabonga:
                    gabonga.resize(round((right-left)*1.3), round((bottom-top)*1.3))
                    # Finds the center location of the image for gabonga to be located
                    centered_x = left + (right-left)//2 - gabonga.width//2
                    centered_y = (top + (bottom-top)//2 - gabonga.height//2)
                    # Composites gabonga on top
                    face.composite(gabonga, left=centered_x, top=centered_y)
                face.save(filename=fname)
        await message.channel.send(content=f"{message.author.mention} I have two words...", file=discord.File(fname))

# Reused code from distort bot but slightly trimmed down
async def grab_file(message: discord.Message):
    types = ["png", "jpg", "jpeg"]
    url = None
    # Finds the URL that the image is at
    if message.embeds:
		# Checks if the embed itself is an image and grabs the url
        if message.embeds[0].url is not None:
            url = message.embeds[0].url
	# Checks to see if the image is a message attachment
    elif message.attachments:
        url = message.attachments[0].url

    else:
        for item in message.content.split(' '):
            if validators.url(item):
                url = item

    if url is None:
        return None

	# Remove the trailing modifiers at the end of the link
    url = url.partition("?")[0]
    
    if not url.endswith(tuple(types)):
        return None

    if validators.url(url):
        fname = requests.utils.urlparse(url)
        fname = f"images/{os.path.basename(fname.path)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with open(fname, "wb") as f:
            with urllib.request.urlopen(req) as r:
                f.write(r.read())
    
    return fname

async def setup(bot: commands.Bot):
  """ Sets up the cog

     Parameters
     -----------
     bot: commands.Bot
        The main cog runners commands.Bot object
  """
  await bot.add_cog(Gabonga(bot))
  print("gabonga: Get gabonganized")