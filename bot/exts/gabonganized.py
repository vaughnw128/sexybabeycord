# Gabonganized.py
# When someone sends a face pic, they get gabonganized. Simple as.
import random

import discord
import face_recognition
from bot import constants
from discord import app_commands
from discord.ext import commands
from wand.image import Image
from bot.utils import file
import os
import logging

log = logging.getLogger("gabonganized")

class Gabonga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.gabonga_menu = app_commands.ContextMenu(
            name="gabonga", callback=self.gabonga_menu
        )
        self.bot.tree.add_command(self.gabonga_menu)

    async def gabonga_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.defer()
        try:
            fname = await file.grab(message)  # Grabs the image
        except Exception:
            await interaction.followup.send(
                "An unexpected error occured while trying to fetch the image."
            )
            return
        if fname is None:
            await interaction.followup.send(
                "The message you tried to gabonga is either not an image, or is of an invalid type."
            )
            return
        elif fname.endswith(".gif"):
            await interaction.followup.send(
                "Gifs are not allowed!"
            )
            return

        try:
            fname = gabonga(fname)
            await interaction.followup.send(
                content="I have two words...", file=discord.File(fname)
            )
            os.remove(fname)
        except Exception:
            await interaction.followup.send(
                "Egads!!! There are no faces in that 'bonga request! Why don't you try another :smirk_cat:"
            )
            return

    @commands.Cog.listener()
    async def on_message(self, message):
        # Checks for the author being the bot
        if message.author.id == constants.Bot.id:
            return

        # Grabs the file using reused distort bot code
        fname = await file.grab(message)
        if fname is None:
            return

        fname = gabonga(fname)

        if fname is not None:
            # Only executes 4% of the time
            if random.randint(0, 100) > 96:
                await message.channel.send(
                    content=f"{message.author.mention} I have two words...",
                    file=discord.File(fname),
                )
                os.remove(fname)


# gabonga
def gabonga(fname: str):
    # Uses face rec to grab the face and get the location
    image = face_recognition.load_image_file(fname)
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 0:
        return None

    # Tries to do multiple faces... might not work
    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        with Image(filename=fname) as face:
            with Image(filename="bot/resources/gabonga.png") as gabonga:
                gabonga.resize(round((right - left) * 1.3), round((bottom - top) * 1.3))
                # Finds the center location of the image for gabonga to be located
                centered_x = left + (right - left) // 2 - gabonga.width // 2
                centered_y = top + (bottom - top) // 2 - gabonga.height // 2
                # Composites gabonga on top
                face.composite(gabonga, left=centered_x, top=centered_y)
            face.save(filename=fname)
    return fname

async def setup(bot: commands.Bot):
    """Sets up the cog

    Parameters
    -----------
    bot: commands.Bot
       The main cog runners commands.Bot object
    """

    if not os.path.exists("bot/resources/images"):
        os.makedirs("bot/resources/images")

    await bot.add_cog(Gabonga(bot))
    log.info("Loaded")
    