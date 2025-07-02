"""Caption

Adds captions to gifs and images with the old iFunny font

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import re
from enum import Enum
from io import BytesIO
import itertools

# external
import discord
from PIL.ImageFont import FreeTypeFont
from discord import app_commands
from discord.app_commands import errors as discord_errors
from discord.ext import commands
from PIL import Image as Image, ImageFont, ImageDraw
from PIL import ImageSequence
from rembg import remove

from sexybabeycord import constants

# project modules
from sexybabeycord.utils import file_helper

log = logging.getLogger("caption")


class CharacterType(Enum):
    English = (1,)
    Japanese = (2,)
    Emoji = (3,)


japanese_ranges = [
    (0x3040, 0x309F),  # Hiragana
    (0x30A0, 0x30FF),  # Katakana
    (0x31F0, 0x31FF),  # Katakana Phonetic Extensions
    (0x4E00, 0x9FFF),  # Common and uncommon Kanji
    (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
    (0xFF66, 0xFF9F),  # Half-width Katakana
]

emoji_ranges = [
    (0x1F600, 0x1F64F),  # Emoticons
    (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
    (0x1F680, 0x1F6FF),  # Transport and Map
    (0x1F1E6, 0x1F1FF),  # Regional country flags
    (0x2600, 0x26FF),  # Misc symbols
    (0x2700, 0x27BF),  # Dingbats
    (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
    (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
    (0x1F700, 0x1F77F),  # Alchemical Symbols
    (0x2300, 0x23FF),  # Miscellaneous Technical
    (0x2B00, 0x2BFF),  # Miscellaneous Symbols and Arrows
]


def wrap_text(text, font, max_width, draw):
    lines = []  # Holds each line in the text box
    current_line = []  # Holds the current line under evaluation.
    current_line_types = []  # Holds the character types for the current line

    words_with_types = split_by_character_class(text)

    for word, char_type in words_with_types:
        # Create a test line by joining words with appropriate spacing
        test_line = ""
        test_words = current_line + [word]
        test_types = current_line_types + [char_type]

        for i, (w, t) in enumerate(zip(test_words, test_types)):
            if i > 0 and t == CharacterType.English and test_types[i-1] == CharacterType.English:
                test_line += " " + w
            else:
                test_line += w

        width = draw.textlength(test_line, font=font)
        if width <= max_width:
            current_line.append(word)
            current_line_types.append(char_type)
        else:
            if current_line:
                final_line = ""
                for i, (w, t) in enumerate(zip(current_line, current_line_types)):
                    if i > 0 and t == CharacterType.English and current_line_types[i-1] == CharacterType.English:
                        final_line += " " + w
                    else:
                        final_line += w
                lines.append(final_line)
            current_line = [word]
            current_line_types = [char_type]

    # Add the last line
    if current_line:
        final_line = ""
        for i, (w, t) in enumerate(zip(current_line, current_line_types)):
            # Only add space before English words that follow another word
            if i > 0 and t == CharacterType.English and current_line_types[i-1] == CharacterType.English:
                final_line += " " + w
            else:
                final_line += w
        lines.append(final_line)

    stripped = [string for string in lines if string.strip("") != ""]

    return stripped


def get_character_class(char):
    code = ord(char)

    if any(start <= code <= end for start, end in emoji_ranges):
        return CharacterType.Emoji
    if any(start <= code <= end for start, end in japanese_ranges):
        return CharacterType.Japanese
    return CharacterType.English


def split_by_character_class(text: str) -> list[tuple[str, CharacterType]]:
    # Create a list of (char, character_class) tuples
    char_tuples = [(char, get_character_class(char)) for char in text]

    # Group consecutive characters of the same type, but handle emojis individually
    result = []
    for character_class, group in itertools.groupby(char_tuples, key=lambda x: x[1]):
        group_list = list(group)
        if character_class == CharacterType.English:
            # Group consecutive non-emoji characters
            chars = "".join(char for char, _ in group_list)
            words = [word.strip() for word in chars.split(" ")]
            # Add each English word with its character type
            for word in words:
                if word:  # Skip empty strings
                    result.append((word, CharacterType.English))
        else:
            # Add each emoji / Japanese as a separate element with its character type
            for char, _ in group_list:
                if char.strip():  # Skip empty strings
                    result.append((char, character_class))

    return result


def get_text_dimensions(text, font) -> tuple[int, int]:
    bbox = font.getbbox(text)
    return (bbox[2] - bbox[0]), (bbox[3] - bbox[1])


def get_fonted_text(multiline_text: list[str], font_size: int = 32):
    # Define the base path for fonts
    fonts_dir = os.path.join("src", "sexybabeycord", "resources", "fonts")

    # Load different fonts
    font_files = {
        CharacterType.English: ImageFont.truetype(os.path.join(fonts_dir, "ifunny.ttf"), font_size),
        CharacterType.Japanese: ImageFont.truetype(os.path.join(fonts_dir, "jp.ttf"), font_size),
        CharacterType.Emoji: ImageFont.truetype(os.path.join(fonts_dir, "emoji.ttf"), font_size),
    }

    # Create char tuples
    char_tuples = [[(char, get_character_class(char)) for char in line] for line in multiline_text]

    classed_multiline_text = []
    for line in char_tuples:
        classed_text = []
        for character_class, group in itertools.groupby(line, key=lambda x: x[1]):
            chars = "".join(char for char, _ in group)
            classed_text.append((chars, character_class))
        classed_multiline_text.append(classed_text)

    fonted_text = [
        [(string, font_files[character_class]) for string, character_class in line] for line in classed_multiline_text
    ]

    return fonted_text


def draw_caption_background(
    bar_height: int,
    image_dimension: tuple[int, int],
    fonted_text: list[list[tuple[str, FreeTypeFont]]],
    line_spacing: int = 4,
) -> Image:
    width, height = (image_dimension[0], bar_height + image_dimension[1])
    image = Image.new("RGBA", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # Calculate total text height including line spacing
    total_text_height = 0
    for line in fonted_text:
        max_height = max(get_text_dimensions(text, font)[1] for text, font in line)
        total_text_height += max_height + line_spacing

    # Remove the extra line spacing after the last line
    if fonted_text:
        total_text_height -= line_spacing

    # Calculate starting_y to center all text vertically in the bar
    starting_y = (bar_height - total_text_height) // 2

    for line in fonted_text:
        # Calculate the total width of the line
        total_width = sum(get_text_dimensions(text, font)[0] for text, font in line)

        # Calculate the starting x position to center the line
        x_position = (width - total_width) / 2

        # Calculate the maximum height of any text segment in this line
        max_height = max(get_text_dimensions(text, font)[1] for text, font in line)

        # Calculate vertical center of the line
        y_center = starting_y + max_height / 2

        # Draw each text segment in the line
        for text, font in line:
            text_width, text_height = get_text_dimensions(text, font)
            text_center_x = x_position + text_width / 2
            draw.text((text_center_x, y_center), text, font=font, fill="black", embedded_color=True, anchor="mm")
            x_position += text_width

        # Move to the next line
        starting_y += max_height + line_spacing

    return image


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
    location = file_helper.cdn_upload(file, ext)
    await interaction.response.send_message(
        content=location,
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
        if (
            not (message.content.lower().startswith("caption") or message.content.lower().startswith("reverse"))
            or message.author.id == self.bot.user.id
        ):
            return

        # Get original message if it is actually a message reply
        try:
            original_message = await message.channel.fetch_message(message.reference.message_id)
        except AttributeError:
            return

        try:
            file, ext = await file_helper.grab_file(original_message)
        except discord_errors.AppCommandError:
            await message.reply("Looks like there was an error grabbing the file :/")
            return

        # Checks filetype
        if ext not in ("png", "jpg", "webp", "gif", "jpeg"):
            await message.reply("Wrong filetype, bozo!!")
            return

        if message.content.lower().startswith("reverse") and ext != "gif":
            await message.reply("You can only reverse gifs, silly ;p.")
            return

        if message.content.lower().startswith("caption"):
            # Gets caption text
            caption_text = re.sub(r"^caption", "", message.content).strip()
            if caption_text is None or len(caption_text) == 0:
                raise discord_errors.AppCommandError("Looks like you didn't add a caption, buddy")

            edited = await caption(file, caption_text, ext)
        elif message.content.lower().startswith("reverse"):
            edited = await caption(file, ext=ext, reversed=True)
        location = file_helper.cdn_upload(edited, ext)
        await message.reply(content=location)


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
    foreground = Image.open(file)

    font_size = foreground.size[0] // 8

    with Image.new(mode="RGB", size=foreground.size) as sizing_im:
        draw = ImageDraw.Draw(sizing_im)
        test_font = ImageFont.truetype("src/sexybabeycord/resources/fonts/ifunny.ttf", font_size)
        multiline_text = wrap_text(caption_text, test_font, sizing_im.size[0] // 2, draw)

    fonted_text = get_fonted_text(multiline_text, font_size)

    # Calculate total text height including line spacing
    line_spacing = 4  # Same as in draw_caption_background
    total_text_height = 0
    for line in fonted_text:
        max_height = max(get_text_dimensions(text, font)[1] for text, font in line)
        total_text_height += max_height + line_spacing

    # Remove the extra line spacing after the last line
    if fonted_text:
        total_text_height -= line_spacing

    # Add some padding to ensure there's enough room
    bar_height = total_text_height + (font_size // 2)
    background = draw_caption_background(bar_height, foreground.size, fonted_text)

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


def get_frame_durations(image: Image, playback_speed: float):
    """Returns the average framerate of a PIL Image object"""
    image.seek(0)
    frames = 0
    durations = []
    while True:
        try:
            frames += 1
            durations.append(image.info["duration"])
            image.seek(image.tell() + 1)
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
