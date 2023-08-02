""" 
    Gabonganized

    Allows users to right click face pictures and 
    gabonganize them, and also has random gabonganizing effects

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import random
import re

# external
import discord
import face_recognition # type: ignore
from discord import app_commands
from discord.ext import commands
from wand.image import Image

# project modules
from bot import constants
from bot.utils import file_helper

log = logging.getLogger("gabonganized")


class Gabonga(commands.Cog):
    """Gabonga class to handle all gabonga requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the 'bonga class and assigns the command tree for the 'bonga menu"""
        self.bot = bot

        self.gabonga_menu = app_commands.ContextMenu(
            name="gabonga", callback=self.gabonga_menu
        )
        self.bot.tree.add_command(self.gabonga_menu)

    async def gabonga_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """Controls the bonga menu"""

        await interaction.response.defer()

        # Grabs the file from the message and checks it
        fname = file_helper.grab(message)  # Grabs the image
        if fname is None:
            await interaction.followup.send(
                "An unexpected error occured while trying to fetch the image."
            )
            log.warning("Image was unable to be fetched")
            return

        if fname.endswith((".png", ".jpg")):
            gabonganized = gabonga(fname)
            if gabonganized is not None:
                log.info(f"Image was succesfully gabonganized: {gabonganized})")
                await interaction.followup.send(
                    content="I have two words...", file=discord.File(gabonganized)
                )
                os.remove(gabonganized)
            else:
                log.info(f"No faces in bonga request: {fname})")
                await interaction.followup.send(
                    "Egads!!! There are no faces in that 'bonga request! Why don't you try another :smirk_cat:"
                )
                os.remove(fname)
        else:
            log.info(f"Wrong filetype rejected: {fname})")
            await interaction.followup.send(
                "Silly fool! 'bonga only works on portable network graphics and and joint photographic experts group :nerd:"
            )
            os.remove(fname)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message gabonga has a 10% chance of gabonganizing someone's face pic"""

        # Uses fixlink's regex to check for twitter first as it will be removed
        link_regex = r"https:\/\/((www.|)tiktok|(www.|)twitter|(www.|)instagram).com([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"

        link = re.search(
            link_regex,
            message.content,
        )

        if link is not None:
            return

        # Checks for the author being the bot
        if message.author.id == constants.Bot.id:
            return

        # Grabs the file using reused distort bot code
        fname = file_helper.grab(message)
        if fname is None:
            return

        if fname is not None and fname.endswith((".png", ".jpg")):
            gabonganized = await gabonga(fname)

            if gabonganized is not None:
                # Only executes 10% of the time
                rand = random.randint(0, 100)
                if rand > 90:
                    await message.channel.send(
                        content=f"{message.author.mention} I have two words...",
                        file=discord.File(gabonganized),
                    )
                    log.info(f"Random 'bonga hit: {rand}")
                else:
                    log.info(f"Random 'bonga miss: {rand}")
                os.remove(gabonganized)
            else:
                os.remove(fname)

async def gabonga(fname: str) -> str:
    """Handles the actual editing work of gabonga"""

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
                # Resize the 'bonga PNG
                gabonga.resize(round((right - left) * 1.3), round((bottom - top) * 1.3))

                # Finds the center location of the image for gabonga to be located
                centered_x = left + (right - left) // 2 - gabonga.width // 2
                centered_y = top + (bottom - top) // 2 - gabonga.height // 2

                # Composites gabonga on top
                face.composite(gabonga, left=centered_x, top=centered_y)
            face.save(filename=fname)
    return fname

async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Gabonga(bot))
    log.info("Loaded")
