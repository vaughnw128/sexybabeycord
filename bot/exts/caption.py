"""
    Caption

    Adds captions to gifs and images with the old iFunny font

    Made with love and care by Vaughn Woerpel
"""


import io

# built-in
import logging
import re
import shutil
import textwrap
import time

# external
import discord
import numpy
from discord import app_commands
from discord.ext import commands
from PIL import Image as PILImage
from PIL import ImageSequence
from wand.color import Color
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image

from bot import constants

# project modules
from bot.utils import file_helper

log = logging.getLogger("caption")


class SelectFont(discord.ui.Select):
    def __init__(self):
        options = []
        for font in constants.Caption.fonts:
            options.append(discord.SelectOption(label=font))
        super().__init__(
            placeholder="Select a font", max_values=1, min_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.font = self.values[0]
        await interaction.response.defer()


class AdvancedCaptionView(discord.ui.View):
    def __init__(self, fname, *, timeout=180):
        self.fname = fname
        self.font = None
        self.reversed = False
        self.caption_text = None
        self.playback_speed = float(1)
        super().__init__(timeout=timeout)
        self.speed_display_button.disabled = True
        if not self.fname.endswith("gif"):
            # self.reverse_button.disabled = True
            self.remove_item(self.reverse_button)

    @discord.ui.button(label="Preview", style=discord.ButtonStyle.blurple, row=4)
    async def preview_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await self.edit_helper(interaction)

    @discord.ui.button(label="Caption", style=discord.ButtonStyle.blurple, row=1)
    async def caption_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(AdvancedCaptionModal(self))

        if SelectFont not in self.children:
            self.add_item(SelectFont())
            await interaction.message.edit(view=self)

    @discord.ui.button(label="⏪", style=discord.ButtonStyle.blurple, row=2)
    async def slow_down_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        self.playback_speed /= 2
        self.speed_display_button.label = f"{self.playback_speed}x"
        await interaction.message.edit(view=self)

    @discord.ui.button(label="1.0x", style=discord.ButtonStyle.gray, row=2)
    async def speed_display_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        return

    @discord.ui.button(label="⏩", style=discord.ButtonStyle.blurple, row=2)
    async def speed_up_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        self.playback_speed *= 2
        self.speed_display_button.label = f"{self.playback_speed}x"
        await interaction.message.edit(view=self)

    @discord.ui.button(label="🔁", style=discord.ButtonStyle.gray, row=2)
    async def reverse_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.reversed:
            self.reversed = False
            button.style = discord.ButtonStyle.gray
            await interaction.response.edit_message(view=self)
        else:
            self.reversed = True
            button.style = discord.ButtonStyle.red
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green, row=4)
    async def go_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await interaction.message.edit(view=None)
        await self.edit_helper(interaction)
        file_helper.remove(self.fname)

    async def on_timeout(self, interaction: discord.Interaction):
        interaction.message.edit("AdvancedCaption has timed out!")
        await interaction.message.edit(view=None)
        file_helper.remove(self.fname)

    async def edit_helper(self, interaction: discord.Interaction):
        temp_filename = self.fname.split(".")[0] + "temp." + self.fname.split(".")[1]
        shutil.copy2(self.fname, temp_filename)
        captioned_file = await caption(
            fname=temp_filename,
            caption_text=self.caption_text,
            font=self.font,
            reversed=self.reversed,
            playback_speed=self.playback_speed,
        )
        await interaction.message.edit(attachments=[discord.File(captioned_file)])
        file_helper.remove(temp_filename)


class AdvancedCaptionModal(discord.ui.Modal, title="Caption"):
    def __init__(self, view, timeout=180):
        self.view = view
        super().__init__(timeout=timeout)

    caption = discord.ui.TextInput(
        label="Caption",
        placeholder="Your caption here...",
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.caption_text = self.caption.value

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        log.error("Advanced caption modal unexpectedly errored out")
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )


class Caption(commands.Cog):
    """Caption class to handle all caption requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the caption class"""
        self.bot = bot
        self.advanced_edit = app_commands.ContextMenu(
            name="Advanced Edit", callback=self.advanced_edit_menu
        )
        self.bot.tree.add_command(self.advanced_edit)

    async def advanced_edit_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        # Grabs and checks file
        fname = file_helper.grab(message)
        if fname is None:
            await interaction.response.send_message(
                "That message had no file", ephemeral=True
            )
            return

        # Checks filetype
        if not fname.endswith((".png", ".jpg", ".gif", ".jpeg")):
            file_helper.remove(fname)
            await interaction.response.send_message(
                "That message has an invalid filetype", ephemeral=True
            )
            return

        await interaction.response.send_message(
            file=discord.File(fname),
            view=AdvancedCaptionView(fname),
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""

        if (
            not message.content.startswith("caption")
            or message.author.id == self.bot.user.id
        ):
            return

        # Get original message if it is actually a message reply
        try:
            original_message = await message.channel.fetch_message(
                message.reference.message_id
            )
        except AttributeError:
            return

        # Gets caption text
        caption_text = re.sub(r"^caption", "", message.content).strip()
        if caption_text is None or len(caption_text) == 0:
            await message.reply("Looks like you didn't add a caption, buddy")
            return None

        response = await caption_helper(original_message, caption_text)

        match response:
            case None:
                return
            case "Original message had no file":
                await message.reply("Are you dumb? that's not even a file")
                return
            case "Invalid filetype":
                await message.reply("That's not an image or a gif :/")
                return
            case "Caption failure":
                log.error(f"Failure while trying to caption image/gif")
                await message.reply("Caption has mysteriously failed")
                return

        log.info(f"Image was succesfully captioned: {response})")
        await message.reply(file=discord.File(response))
        file_helper.remove(response)


async def caption_helper(message: discord.Message, caption_text: str) -> str:
    """Helper method for captioning, allows for testing"""

    # Grabs and checks file
    fname = file_helper.grab(message)
    if fname is None:
        return "Original message had no file"

    # Checks filetype
    if not fname.endswith((".png", ".jpg", ".gif", ".jpeg")):
        file_helper.remove(fname)
        return "Invalid filetype"

    try:
        captioned = await caption(fname, caption_text)
        return captioned
    except Exception:
        file_helper.remove(fname)
        return "Caption failure"


async def caption(
    fname: str,
    caption_text: str,
    font: str | None = None,
    reversed: bool | None = False,
    playback_speed: float | None = 1.0,
) -> str:
    """Adds a caption to images and gifs with image_magick"""

    foreground = PILImage.open(fname)

    x, y = foreground.size

    wrapper = textwrap.TextWrapper(width=50)
    wrapper_split_length = len(wrapper.wrap(text=caption_text))
    bar_height = wrapper_split_length * round(y / 5)

    with Image(width=x, height=y + bar_height) as template_image:
        with Drawing() as context:
            context.fill_color = "white"
            context.rectangle(left=0, top=0, width=x, height=bar_height)

            if font is None:
                font = "ifunny.otf"
            font = Font(path=constants.Caption.fontdir + font)

            context(template_image)
            template_image.caption(
                caption_text,
                left=0,
                top=0,
                width=x,
                height=bar_height,
                font=font,
                gravity="center",
            )

        img_buffer = numpy.asarray(
            bytearray(template_image.make_blob(format="png")), dtype="uint8"
        )
        bytesio = io.BytesIO(img_buffer)
        background = PILImage.open(bytesio).convert("RGBA")

    if foreground.is_animated:
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(foreground):
            captioned = background.copy()
            captioned.paste(frame, (0, bar_height))
            frames.append(captioned)
            durations.append(20)

        if reversed:
            frames.reverse()

        # print(durations)

        frames[0].save(
            fname,
            save_all=True,
            append_images=frames,
            loop=0,
            duration=1,
        )
    else:
        background.paste(foreground, (0, bar_height))
        background.save(fname)

    return fname


def get_avg_fps(PIL_Image_object):
    """Returns the average framerate of a PIL Image object"""
    PIL_Image_object.seek(0)
    frames = duration = 0
    while True:
        try:
            frames += 1
            duration += PIL_Image_object.info["duration"]
            PIL_Image_object.seek(PIL_Image_object.tell() + 1)
        except EOFError:
            return frames / duration * 1000
    return None


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Caption(bot))
    log.info("Loaded")
