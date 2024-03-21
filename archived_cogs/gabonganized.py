"""Gabonganized

Allows users to right click face pictures and
gabonganize them, and also has random gabonganizing effects

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
from io import BytesIO

# external
import discord
import discord.app_commands.errors as discord_errors
import mediapipe as mp
import numpy as np
from discord import app_commands
from discord.ext import commands
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image

# project modules
from bot.utils import file_helper

base_options = python.BaseOptions(model_asset_path="./bot/resources/blaze_face_short_range.tflite")
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
        gabonganized = await gabonganize(file, ext, face_locations)
        await interaction.followup.send(
            content="I have two words...", file=discord.File(fp=gabonganized, filename=f"gabonganized.{ext}"),
        )


async def gabonganize(file: BytesIO, ext: str, face_locations: list) -> BytesIO:
    """Handles the actual editing work of gabonga"""
    with Image.open(fp=file) as face:
        with Image.open(fp="bot/resources/gabonga.png") as gabonga:
            # Tries to do multiple faces... might not work
            for face_location in face_locations:
                # Print the location of each face in this image
                x, y, w, h = face_location

                # Resize the 'bonga PNG
                gabonga.resize((w, h))

                # Composites gabonga on top
                face.paste(gabonga, (x, y))
            buf = BytesIO()
            face.save(buf, format=ext)
            buf.seek(0)
            return buf


def get_faces(file: BytesIO) -> list[tuple[int, int, int, int]] | None:
    pil_img = Image.open(file)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(pil_img))
    detection_result = detector.detect(image).detections
    if not detection_result:
        raise discord_errors.AppCommandError("No faces to 'bonga!")
    boxes = []
    for detection in detection_result:
        box = detection.bounding_box
        boxes.append((box.origin_x, box.origin_y, box.width, box.height))
    return boxes


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(Gabonga(bot))
    log.info("Loaded")
