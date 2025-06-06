"""Present

Makes Asher present on the image you send him

Code blatently stolen and reused by Ian Le
"""

# built-in
import logging
from io import BytesIO
from itertools import chain

# external
import discord
from discord.ext import commands
from wand.image import Image
from discord import app_commands


# project modules
from sexybabeycord.utils import file_helper

log = logging.getLogger("present")


class Present(commands.Cog):
    """A Discord Cog to handle image distortion"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the command context menu"""
        self.bot = bot
        self.distort_menu = app_commands.ContextMenu(name="present", callback=self.present_ctx)
        self.bot.tree.add_command(self.distort_menu)

    async def present_ctx(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Build the distort context menu"""
        await interaction.response.defer()
        file, ext = await file_helper.grab_file(message)
        distorted = await present(file, ext)

        await interaction.followup.send(file=discord.File(fp=distorted, filename=f"distort.{ext}"))


async def present(
    file: BytesIO,
    ext: str | None = None,
) -> BytesIO:
    """Make Asher present on the image"""

    buf = BytesIO()

    with Image(file=file) as present_image:
        with Image(filename="src/sexybabeycord/resources/asher.jpg") as background:
            source_points = (
                (0, 0),
                (present_image.width, 0),
                (0, present_image.height),
                (present_image.width, present_image.height),
            )
            destination_points = ((1600, 460), (3240, 0), (1600, 2000), (3240, 1980))

            order = chain.from_iterable(zip(source_points, destination_points))
            arguments = list(chain.from_iterable(order))

            present_image.virtual_pixel = "transparent"
            present_image.artifacts["distort:viewport"] = f"{background.width}x{background.height}+0+0"

            # Apply the perspective distortion to the blank image
            present_image.distort("perspective", arguments)

            # Composite the distorted source onto the background
            background.composite(present_image, 0, 0)

            # Save the resulting image
            background.save(file=buf)

        buf.seek(0)
        return buf


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(Present(bot))
    log.info("Loaded")
