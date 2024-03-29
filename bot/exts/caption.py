"""Caption

Adds captions to gifs and images with the old iFunny font

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import re
import textwrap
from io import BytesIO

# external
import discord
import numpy
from discord import app_commands
from discord.app_commands import errors as discord_errors
from discord.ext import commands
from PIL import Image as PILImage
from PIL import ImageSequence
from rembg import remove
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
        for font in constants.Caption.fonts.keys():
            options.append(discord.SelectOption(label=font))
        super().__init__(placeholder="Select a font", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.font = self.values[0]
        await interaction.response.defer()


class AdvancedCaptionView(discord.ui.View):
    def __init__(self, file, ext, *, timeout=180):
        self.file = file
        self.ext = ext
        self.font = None
        self.reversed = False
        self.caption_text = None
        self.playback_speed = float(1)
        self.remove_bg = False
        super().__init__(timeout=timeout)
        self.speed_display_button.disabled = True
        if ext == "gif":
            self.remove_item(self.remove_bg_button)
        else:
            self.remove_item(self.slow_down_button)
            self.remove_item(self.speed_display_button)
            self.remove_item(self.speed_up_button)
            self.remove_item(self.reverse_button)

    @discord.ui.button(label="Preview", style=discord.ButtonStyle.blurple, row=4)
    async def preview_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.edit_helper(interaction)

    @discord.ui.button(label="Caption", style=discord.ButtonStyle.blurple, row=1)
    async def caption_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AdvancedCaptionModal(self))

        if "SelectFont" not in "".join(str(self.children)):
            self.add_item(SelectFont())
            await interaction.message.edit(view=self)

    @discord.ui.button(label="🌁", style=discord.ButtonStyle.gray, row=1)
    async def remove_bg_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.remove_bg:
            self.remove_bg = False
            button.style = discord.ButtonStyle.gray
            await interaction.response.edit_message(view=self)
        else:
            self.remove_bg = True
            button.style = discord.ButtonStyle.red
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="⏪", style=discord.ButtonStyle.blurple, row=2)
    async def slow_down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.playback_speed /= 2
        self.speed_display_button.label = f"{self.playback_speed}x"
        await interaction.message.edit(view=self)

    @discord.ui.button(label="1.0x", style=discord.ButtonStyle.gray, row=2)
    async def speed_display_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label="⏩", style=discord.ButtonStyle.blurple, row=2)
    async def speed_up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.playback_speed *= 2
        self.speed_display_button.label = f"{self.playback_speed}x"
        await interaction.message.edit(view=self)

    @discord.ui.button(label="🔁", style=discord.ButtonStyle.gray, row=2)
    async def reverse_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.reversed:
            self.reversed = False
            button.style = discord.ButtonStyle.gray
            await interaction.response.edit_message(view=self)
        else:
            self.reversed = True
            button.style = discord.ButtonStyle.red
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green, row=4)
    async def go_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.edit(view=None)
        await self.edit_helper(interaction)

    async def on_timeout(self, interaction: discord.Interaction):
        await interaction.message.edit("AdvancedCaption has timed out!")
        await interaction.message.edit(view=None)

    async def edit_helper(self, interaction: discord.Interaction):
        self.file.seek(0)
        captioned_file = await caption(
            file=self.file,
            caption_text=self.caption_text,
            ext=self.ext,
            font=self.font,
            reversed=self.reversed,
            playback_speed=self.playback_speed,
            remove_bg=self.remove_bg,
        )
        await interaction.message.edit(attachments=[discord.File(fp=captioned_file, filename=f"captioned.{self.ext}")])


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

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        log.error("Advanced caption modal unexpectedly errored out")
        await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)


async def advanced_edit_menu(interaction: discord.Interaction, message: discord.Message) -> None:
    # Grabs and checks file
    file, ext = await file_helper.grab_file(message)

    # Checks filetype
    if ext not in ("png", "jpg", "gif", "jpeg"):
        await interaction.response.send_message("That message has an invalid filetype", ephemeral=True)
        return

    await interaction.response.send_message(
        file=discord.File(fp=file, filename=f"advanced-edit.{ext}"),
        view=AdvancedCaptionView(file, ext),
    )


class Caption(commands.Cog):
    """Caption class to handle all caption requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the caption class"""
        self.bot = bot
        self.advanced_edit = app_commands.ContextMenu(name="Advanced Edit", callback=advanced_edit_menu)
        self.bot.tree.add_command(self.advanced_edit)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""
        if not message.content.startswith("caption") or message.author.id == self.bot.user.id:
            return

        # Get original message if it is actually a message reply
        try:
            original_message = await message.channel.fetch_message(message.reference.message_id)
        except AttributeError:
            return
        # Gets caption text
        caption_text = re.sub(r"^caption", "", message.content).strip()
        if caption_text is None or len(caption_text) == 0:
            raise discord_errors.AppCommandError("Looks like you didn't add a caption, buddy")

        try:
            file, ext = await file_helper.grab_file(original_message)
        except discord_errors.AppCommandError:
            await message.reply("Looks like there was an error grabbing the file :/")
            return
        # Checks filetype
        if ext not in ("png", "jpg", "webp", "gif", "jpeg"):
            await message.reply("Wrong filetype, bozo!!")
            return

        captioned = await caption(file, caption_text, ext)
        await message.reply(file=discord.File(fp=captioned, filename=f"captioned.{ext}"))


async def caption(
    file: BytesIO,
    caption_text: str | None = None,
    ext: str | None = None,
    font: str | None = None,
    reversed: bool | None = False,
    playback_speed: float | None = 1.0,
    remove_bg: bool | None = False,
) -> BytesIO:
    """Adds a caption to images and gifs with image_magick"""
    buf = BytesIO()
    foreground = PILImage.open(file)

    x, y = foreground.size

    bar_height = 0
    if caption_text:
        wrapper = textwrap.TextWrapper(width=50)
        wrapper_split_length = len(wrapper.wrap(text=caption_text))
        bar_height = wrapper_split_length * round(y / 5)

        with Image(width=x, height=y + bar_height) as template_image:
            with Drawing() as context:
                context.fill_color = "white"
                context.rectangle(left=0, top=0, width=x, height=bar_height)

                if font is None:
                    font = "default"
                font = Font(path=constants.Caption.fonts[font])

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

            img_buffer = numpy.asarray(bytearray(template_image.make_blob(format="png")), dtype="uint8")
            bytesio = BytesIO(img_buffer)
            background = PILImage.open(bytesio).convert("RGBA")
    else:
        background = PILImage.new("RGBA", (x, y), (255, 255, 255))

    if ext == "gif":
        frames = []
        for frame in ImageSequence.Iterator(foreground):
            captioned = background.copy()
            captioned.paste(frame, (0, bar_height))
            frames.append(captioned)

        if reversed:
            frames.reverse()

        durations = get_frame_durations(foreground, playback_speed)
        frames[0].save(
            buf,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=durations,
        )
    else:
        if remove_bg:
            foreground = remove(foreground)
        background.paste(foreground, (0, bar_height))
        background.save(buf, format="PNG")

    buf.seek(0)
    return buf


def get_frame_durations(PIL_Image_object: PILImage, playback_speed: float):
    """Returns the average framerate of a PIL Image object"""
    PIL_Image_object.seek(0)
    frames = 0
    durations = []
    while True:
        try:
            frames += 1
            durations.append(PIL_Image_object.info["duration"])
            PIL_Image_object.seek(PIL_Image_object.tell() + 1)
        except EOFError:
            for i in range(len(durations)):
                duration = durations[i]
                if duration == 0:
                    duration = 100
                duration = duration / playback_speed

                if duration < 20:
                    duration = 20
                elif duration > 1000:
                    duration = 1000
                durations[i] = int(round(duration))
            return durations


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    await bot.add_cog(Caption(bot))
    log.info("Loaded")
