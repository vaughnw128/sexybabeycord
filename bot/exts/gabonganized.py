"""
Gabonganized

Allows users to right click face pictures and
gabonganize them, and also has random gabonganizing effects

Made with love and care by Vaughn Woerpel
"""

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# built-in
import logging
from io import BytesIO

# external
import discord
from discord import app_commands
from discord.ext import commands
from wand.image import Image
import cv2
from PIL import Image
import numpy as np

# project modules
from bot.utils import file_helper

base_options = python.BaseOptions(model_asset_path='./bot/resources/blaze_face_short_range.tflite')
options = vision.FaceDetectorOptions(base_options=base_options)
detector = vision.FaceDetector.create_from_options(options)

log = logging.getLogger("gabonganized")


class Gabonga(commands.Cog):
    """Gabonga class to handle all gabonga requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the 'bonga class and assigns the command tree for the 'bonga menu"""
        self.bot = bot

        self.gabonga_menu = app_commands.ContextMenu(name="gabonga", callback=self.gabonga_menu)
        self.bot.tree.add_command(self.gabonga_menu)

    async def gabonga_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Controls the bonga menu"""

        await interaction.response.defer()
        file, ext = await file_helper.grab_file(message)
        face_locations = get_faces(file)
        # if len(face_locations) == 0:
        #     await interaction.followup.send("No faces to 'bonga, bro!")
        # try:
        #     gabonganized = await gabonganize(file, face_locations)
        # except Exception:
        #     await interaction.followup.send("Unexpected 'bonga error : (")
        # await interaction.followup.send(content="I have two words...", file=discord.File(fp=gabonganized, filename=f"gabonganized.{ext}"))

async def gabonganize(fname: str, face_locations: list) -> BytesIO:
    """Handles the actual editing work of gabonga"""

    with Image(filename=fname) as face:
        with Image(filename="bot/resources/gabonga.png") as gabonga:
            # Tries to do multiple faces... might not work
            for face_location in face_locations:
                # Print the location of each face in this image
                x, y, w, h = face_location

                # Resize the 'bonga PNG
                gabonga.resize(w, h)

                # Composites gabonga on top
                face.composite(gabonga, left=x, top=y)
            buf = BytesIO()
            face.save(file=buf)
            buf.seek(0)
            return buf

def get_faces(file: BytesIO) -> None:
    pil_img = Image.open(file)
    image = mp.Image(
        image_format=mp.ImageFormat.SRGB, data=np.asarray(pil_img))
    detection_result = detector.detect(image)
    print(detection_result)


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Gabonga(bot))
    log.info("Loaded")
