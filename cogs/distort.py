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
        try:
            fname = await grab_file(message) # Grabs the image
        except Exception:
            await interaction.followup.send("An unexpected error occured while trying to fetch the image.")
            return
        if fname is None:
            await interaction.followup.send("The message you tried to distort is either not an image, or is of an invalid type.")
            return

        try:
            distort(fname)
        except Exception:
            await interaction.followup.send("An unexpected error occured while trying to distort the image.")
            return
        
        await interaction.followup.send("Done!")
        await interaction.channel.send(file=discord.File(fname), view=DistortView(fname))

    
# View setup for the buttons
class DistortView(discord.ui.View):
    def __init__(self, fname):
        super().__init__()
        self.fname = fname

    @discord.ui.button(label="Distort", style=discord.ButtonStyle.green)
    async def distort_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        distort(self.fname)
        await interaction.message.edit(attachments=[discord.File(self.fname)])
        await interaction.response.defer()
    
    @discord.ui.button(label="Lock", style=discord.ButtonStyle.red)
    async def lock_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.response.edit_message(view=None)

def distort(fname: str):
    with Image(filename=fname) as temp_img:
        if fname.endswith('gif'):
            with Image() as dst_image:
                with Image(filename=fname) as src_image:
                    src_image.coalesce()
                    for i,frame in enumerate(src_image.sequence):
                        frameimage = Image(image=frame)
                        x, y = frame.width, frame.height
                        if x > 1 and y > 1:
                            frameimage.liquid_rescale(round(x*.60), round(y*.60))
                            frameimage.resize(x,y)
                            dst_image.sequence.append(frameimage)
                dst_image.optimize_layers()
                dst_image.optimize_transparency()
                dst_image.save(filename=fname)
        else:
            x, y = temp_img.width, temp_img.height
            temp_img.liquid_rescale(round(x*.60), round(y*.60))
            temp_img.resize(x,y)
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