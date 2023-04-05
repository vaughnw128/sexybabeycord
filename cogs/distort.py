import discord, logging, json
from discord.ext import commands
from config import tenorkey
from wand.image import Image
from discord import app_commands
from discord.ext import commands
import urllib
import requests
import os
from os import sys
from wand.color import Color
import imghdr
import validators
import ffmpy
import urllib 
import re

class Distort(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.distort_menu = app_commands.ContextMenu(
                name = "distort",
                callback=self.distort_ctx
            )
        self.bot.tree.add_command(self.distort_menu)

    async def distort_ctx(self, interaction: discord.Interaction, message: discord.Message):

        await interaction.response.defer(ephemeral=True)

        fname = await grab_file(message) # Grabs the image
        if fname is None:
            await interaction.followup.send("The message you tried to distort is either not an image, or is of an invalid type.")
            return

        print(fname)

        distort(fname)
        await interaction.followup.send("Done!")
        await interaction.channel.send(file=discord.File(fname))


def distort(fname: str):
    
    with Image(filename=fname) as temp_img:
        if fname.endswith('gif'):
            # with Image() as new:
            #     with Image(filename=fname) as source:
            #         for frame in source.sequence:
            #             if frame.width > 1 and frame.height > 1:
            #                 x, y = frame.width, frame.height
                            
            #                 frame.resize(x, y)
            #                 new.sequence.append(frame)
            with Image() as dst_image:
                with Image(filename=fname) as src_image:
                    for frame in src_image.sequence:
                        if frame.width > 1 and frame.height > 1:
                            x, y = frame.width, frame.height
                            frame.liquid_rescale(x//2, y//2)
                            frame.resize(x, y)
                            dst_image.sequence.append(frame)
                dst_image.save(filename=fname)
            with Image(filename=fname) as img:      
                debug_layers(img, 'layers-expanded.png')
                # new.type = 'optimize'
                # new.save(filename=fname)
        else:
            temp_img.liquid_rescale(round(temp_img.width*.60), round(temp_img.height*.60))
            temp_img.save(filename=fname)
    

async def grab_file(message: discord.Message):
    types = ["png", "jpg", "jpeg", "gif", "mp4"]
    url = None
    # Finds the URL that the image is at
    if message.embeds:
		# Checks if the embed itself is an image and grabs the url
        if message.embeds[0].url is not None:
            url = message.embeds[0].url
		# Checks if the embed is a video (tenor gif) and grabs the url
        elif message.embeds[0].video.url is not None:
            url = message.embeds[0].video.url
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

    if "tenor" in url:
        print(url)
        id = url.split("-")[len(url.split("-"))-1]
        resp = requests.get(f"https://tenor.googleapis.com/v2/posts?key={tenorkey}&ids={id}&limit=1")
        data = resp.json()
        url = data['results'][0]['media_formats']['mediumgif']['url']
    
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

def debug_layers(image, output):
    print('Debugging to file', output)
    with Image(image) as img:
        img.background_color = Color('lime')
        for index, frame in enumerate(img.sequence):
            print('Frame {0} size : {1} page: {2}'.format(index,
                                                          frame.size,
                                                          frame.page))
        img.concat(stacked=True)
        img.save(filename=output)

async def setup(bot: commands.Bot):
    """ Sets up the cog

        Parameters
        -----------
        bot: commands.Bot
        The main cog runners commands.Bot object
    """

    # Adds the cog and reports that it's loaded
    await bot.add_cog(Distort(bot))
    print("Distort: I'm loaded 👺")