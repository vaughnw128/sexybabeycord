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
from typing import List, Optional, Tuple

# external
import discord
from PIL.ImageFont import FreeTypeFont
from discord.app_commands import errors as discord_errors
from discord.ext import commands
from PIL import Image as Image, ImageFont, ImageDraw
from PIL import ImageSequence
from rembg import remove


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


def wrap_text(text: str, font: FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> List[str]:
    """Wrap text considering different character types and their respective fonts"""
    lines = []
    current_line = []
    current_line_types = []

    words_with_types = split_by_character_class(text)

    for word, char_type in words_with_types:
        test_line = ""
        test_words = current_line + [word]
        test_types = current_line_types + [char_type]

        for i, (w, t) in enumerate(zip(test_words, test_types)):
            if i > 0 and t == CharacterType.English and test_types[i - 1] == CharacterType.English:
                test_line += " " + w
            else:
                test_line += w

        width = calculate_line_width(test_words, test_types, font)
        if width <= max_width:
            current_line.append(word)
            current_line_types.append(char_type)
        else:
            if current_line:
                final_line = ""
                for i, (w, t) in enumerate(zip(current_line, current_line_types)):
                    if i > 0 and t == CharacterType.English and current_line_types[i - 1] == CharacterType.English:
                        final_line += " " + w
                    else:
                        final_line += w
                lines.append(final_line)
            current_line = [word]
            current_line_types = [char_type]

    if current_line:
        final_line = ""
        for i, (w, t) in enumerate(zip(current_line, current_line_types)):
            if i > 0 and t == CharacterType.English and current_line_types[i - 1] == CharacterType.English:
                final_line += " " + w
            else:
                final_line += w
        lines.append(final_line)

    stripped = [string for string in lines if string.strip("") != ""]

    return stripped


def calculate_line_width(words: List[str], types: List[CharacterType], base_font: FreeTypeFont) -> int:
    """Calculate the width of a line considering different character types"""
    total_width = 0
    fonts_dir = os.path.join("src", "sexybabeycord", "resources", "fonts")
    font_size = base_font.size

    fonts = {
        CharacterType.English: ImageFont.truetype(os.path.join(fonts_dir, "ifunny.ttf"), font_size),
        CharacterType.Japanese: ImageFont.truetype(os.path.join(fonts_dir, "jp.ttf"), font_size),
        CharacterType.Emoji: ImageFont.truetype(os.path.join(fonts_dir, "emoji.ttf"), font_size),
    }

    for i, (word, char_type) in enumerate(zip(words, types)):
        font = fonts[char_type]
        word_width = get_text_dimensions(word, font)[0]

        if i > 0 and char_type == CharacterType.English and types[i - 1] == CharacterType.English:
            space_width = get_text_dimensions(" ", font)[0]
            total_width += space_width

        total_width += word_width

    return total_width


def get_character_class(char: str) -> CharacterType:
    code = ord(char)

    if any(start <= code <= end for start, end in emoji_ranges):
        return CharacterType.Emoji
    if any(start <= code <= end for start, end in japanese_ranges):
        return CharacterType.Japanese
    return CharacterType.English


def split_by_character_class(text: str) -> List[Tuple[str, CharacterType]]:
    char_tuples = [(char, get_character_class(char)) for char in text]

    result = []
    for character_class, group in itertools.groupby(char_tuples, key=lambda x: x[1]):
        group_list = list(group)
        if character_class == CharacterType.English:
            chars = "".join(char for char, _ in group_list)
            words = [word.strip() for word in chars.split(" ")]
            for word in words:
                if word:
                    result.append((word, CharacterType.English))
        else:
            for char, _ in group_list:
                if char.strip():
                    result.append((char, character_class))

    return result


def calculate_optimal_font_size(image_width: int, text: str) -> int:
    """Calculate the optimal font size that ensures all character types fit within the image width"""
    if not text:
        return image_width // 10

    fonts_dir = os.path.join("src", "sexybabeycord", "resources", "fonts")

    base_font_size = image_width // 10
    max_width = image_width * 0.7

    min_size = max(base_font_size // 4, 12)
    max_size = base_font_size

    optimal_size = min_size

    while min_size <= max_size:
        font_size = (min_size + max_size) // 2

        try:
            fonts = {
                CharacterType.English: ImageFont.truetype(os.path.join(fonts_dir, "ifunny.ttf"), font_size),
                CharacterType.Japanese: ImageFont.truetype(os.path.join(fonts_dir, "jp.ttf"), font_size),
                CharacterType.Emoji: ImageFont.truetype(os.path.join(fonts_dir, "emoji.ttf"), font_size),
            }

            words_with_types = split_by_character_class(text)
            current_line_width = 0
            fits = True

            for word, char_type in words_with_types:
                font = fonts[char_type]
                word_width = get_text_dimensions(word, font)[0]

                if char_type == CharacterType.English and current_line_width > 0:
                    space_width = get_text_dimensions(" ", font)[0]
                    if current_line_width + space_width + word_width <= max_width:
                        current_line_width += space_width + word_width
                    else:
                        current_line_width = word_width
                else:
                    if current_line_width + word_width <= max_width:
                        current_line_width += word_width
                    else:
                        current_line_width = word_width

                if word_width > max_width:
                    fits = False
                    break

            if fits:
                optimal_size = font_size
                min_size = font_size + 1
            else:
                max_size = font_size - 1

        except Exception:
            max_size = font_size - 1

    return optimal_size


def get_text_dimensions(text: str, font: FreeTypeFont) -> Tuple[int, int]:
    bbox = font.getbbox(text)
    return (bbox[2] - bbox[0]), (bbox[3] - bbox[1])


def get_fonted_text(multiline_text: List[str], font_size: int = 24) -> List[List[Tuple[str, FreeTypeFont]]]:
    fonts_dir = os.path.join("src", "sexybabeycord", "resources", "fonts")

    font_files = {
        CharacterType.English: ImageFont.truetype(os.path.join(fonts_dir, "ifunny.ttf"), font_size),
        CharacterType.Japanese: ImageFont.truetype(os.path.join(fonts_dir, "jp.ttf"), font_size),
        CharacterType.Emoji: ImageFont.truetype(os.path.join(fonts_dir, "emoji.ttf"), font_size),
    }

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
    image_dimension: Tuple[int, int],
    fonted_text: List[List[Tuple[str, FreeTypeFont]]],
    line_spacing: int = 4,
) -> Image:
    width, height = (image_dimension[0], bar_height + image_dimension[1])
    image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rectangle([0, 0, width, bar_height], fill="white")

    total_text_height = 0
    for line in fonted_text:
        max_height = max(get_text_dimensions(text, font)[1] for text, font in line)
        total_text_height += max_height + line_spacing

    if fonted_text:
        total_text_height -= line_spacing

    starting_y = (bar_height - total_text_height) // 2

    for line in fonted_text:
        total_width = sum(get_text_dimensions(text, font)[0] for text, font in line)
        x_position = (width - total_width) / 2
        max_height = max(get_text_dimensions(text, font)[1] for text, font in line)
        y_center = starting_y + max_height / 2

        for text, font in line:
            text_width, text_height = get_text_dimensions(text, font)
            text_center_x = x_position + text_width / 2
            draw.text((text_center_x, y_center), text, font=font, fill="black", embedded_color=True, anchor="mm")
            x_position += text_width

        starting_y += max_height + line_spacing

    return image


class Caption(commands.Cog):
    """Caption class to handle all caption requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the caption class"""
        self.bot = bot
        log.info("Caption cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""
        if (
            not (message.content.lower().startswith("caption") or message.content.lower().startswith("reverse"))
            or message.author.id == self.bot.user.id
        ):
            return

        log.debug(f"Caption/reverse command from {message.author} in {message.channel}")

        try:
            original_message = await message.channel.fetch_message(message.reference.message_id)
        except AttributeError:
            log.debug(f"No message reference found for caption command from {message.author}")
            return

        try:
            file, ext = await file_helper.grab_file(original_message)
            log.debug(f"Retrieved file with extension: {ext}")
        except discord_errors.AppCommandError as e:
            log.error(f"Failed to grab file for caption command from {message.author}: {e}")
            await message.reply("Looks like there was an error grabbing the file :/")
            return

        if ext not in ("png", "jpg", "webp", "gif", "jpeg"):
            log.warning(f"Invalid file type for caption: {ext} from {message.author}")
            await message.reply("Wrong filetype, bozo!!")
            return

        if message.content.lower().startswith("reverse") and ext != "gif":
            log.warning(f"Reverse command used on non-GIF file: {ext} from {message.author}")
            await message.reply("You can only reverse gifs, silly ;p.")
            return

        try:
            if message.content.lower().startswith("caption"):
                caption_text = re.sub(r"^(?i)caption", "", message.content).strip()
                if caption_text is None or len(caption_text) == 0:
                    raise discord_errors.AppCommandError("Looks like you didn't add a caption, buddy")

                log.debug(f"Processing caption: '{caption_text[:50]}...' for {message.author}")
                edited = await caption(file, caption_text, ext)
            elif message.content.lower().startswith("reverse"):
                log.debug(f"Processing reverse for {message.author}")
                edited = await caption(file, ext=ext, reversed=True)

            location = file_helper.cdn_upload(edited, ext)
            await message.reply(content=location)
            log.info(f"Successfully processed caption command for {message.author}")

        except Exception as e:
            log.error(f"Failed to process caption command for {message.author}: {e}")
            await message.reply("Failed to process caption")


async def caption(
    file: BytesIO,
    caption_text: Optional[str] = None,
    ext: Optional[str] = None,
    font: Optional[str] = None,
    reversed: bool = False,
    playback_speed: float = 1.0,
    remove_bg: bool = False,
) -> BytesIO:
    """Adds a caption to images and gifs with image_magick"""
    log.debug(
        f"Starting caption processing - ext: {ext}, reversed: {reversed}, speed: {playback_speed}, remove_bg: {remove_bg}"
    )
    buf = BytesIO()
    foreground = Image.open(file)

    font_size = calculate_optimal_font_size(foreground.size[0], caption_text)
    log.debug(f"Calculated optimal font size: {font_size}")

    with Image.new(mode="RGBA", size=foreground.size, color=(0, 0, 0, 0)) as sizing_im:
        draw = ImageDraw.Draw(sizing_im)
        test_font = ImageFont.truetype("src/sexybabeycord/resources/fonts/ifunny.ttf", font_size)
        multiline_text = wrap_text(caption_text, test_font, sizing_im.size[0] * 0.7, draw)

    fonted_text = get_fonted_text(multiline_text, font_size)

    line_spacing = 4
    total_text_height = 0
    for line in fonted_text:
        max_height = max(get_text_dimensions(text, font)[1] for text, font in line)
        total_text_height += max_height + line_spacing

    if fonted_text:
        total_text_height -= line_spacing

    bar_height = total_text_height + (font_size // 2)
    background = draw_caption_background(bar_height, foreground.size, fonted_text)

    if ext == "gif":
        log.debug("Processing GIF caption")
        frames = []
        for frame in ImageSequence.Iterator(foreground):
            frame_rgba = frame.convert("RGBA")
            captioned = background.copy()
            if frame_rgba.size != foreground.size:
                frame_rgba = frame_rgba.resize(foreground.size, Image.Resampling.LANCZOS)
            captioned.paste(frame_rgba, (0, bar_height), frame_rgba)
            frames.append(captioned)

        if reversed:
            frames.reverse()
            log.debug("Reversed GIF frames")

        durations = get_frame_durations(foreground, playback_speed)
        frames[0].save(
            buf,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=durations,
            optimize=False,
            disposal=2,
        )
        log.debug(f"Saved GIF with {len(frames)} frames")
    else:
        log.debug("Processing static image caption")
        if remove_bg:
            log.debug("Removing background from image")
            foreground = remove(foreground)
        background.paste(foreground, (0, bar_height))
        background.save(buf, format="PNG")
        log.debug("Saved PNG image")

    buf.seek(0)
    log.info("Caption processing completed successfully")
    return buf


def get_frame_durations(image: Image, playback_speed: float) -> List[int]:
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
    try:
        await bot.add_cog(Caption(bot))
        log.info("Caption cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load Caption cog: {e}")
        raise
