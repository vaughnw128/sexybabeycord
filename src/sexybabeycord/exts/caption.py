"""Caption

Adds captions to gifs and images using the caption Rust library.

Made with love and care by Vaughn Woerpel
"""

# built-in
import asyncio
import logging
import re
import time
from io import BytesIO

# external
import discord
from discord.app_commands import errors as discord_errors
from discord.ext import commands
import caption as fast_caption

# project
from sexybabeycord.utils import file_helper

log = logging.getLogger("caption")


class Caption(commands.Cog):
    """Caption class to handle all caption requests"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes the caption class"""

        self.bot = bot
        self._captioner = fast_caption.Captioner()
        log.info("Caption cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """On message if someone says 'caption' it adds the caption to the image it's replying to"""

        text = message.content.lower()

        if (
            not (text.startswith("caption") or text.startswith("dcaption"))
            or message.author.id == self.bot.user.id
        ):
            return

        log.debug(f"Caption command from {message.author} in {message.channel}")

        try:
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

            caption_text = re.sub(r"(?i)^(d|)caption", "", message.content).strip()
            if not caption_text:
                await message.reply("Looks like you didn't add a caption, buddy")
                return

            log.debug(f"Processing caption: '{caption_text[:50]}' for {message.author}")

            input_bytes = file.read()
            input_kb = len(input_bytes) / 1024
            output_format = "gif" if ext == "gif" else "png"

            captioner = self._captioner
            t0 = time.perf_counter()
            captioned_bytes: bytes = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: captioner.caption_bytes(input_bytes, caption_text, output_format),
            )
            caption_ms = (time.perf_counter() - t0) * 1000

            t1 = time.perf_counter()
            location = await file_helper.cdn_upload(BytesIO(captioned_bytes), output_format)
            upload_ms = (time.perf_counter() - t1) * 1000

            await message.reply(content=location)
            log.info(
                f"Captioned {ext} ({input_kb:.1f} KB) for {message.author} in "
                f"{caption_ms:.0f}ms caption / {upload_ms:.0f}ms upload"
            )

            if text.startswith("dcaption"):
                try:
                    if original_message.author.id == message.author.id:
                        await original_message.delete()
                    await message.delete()
                except Exception as e:
                    log.error(f"Failed to delete original message for dcaption command from {message.author}: {e}")

        except Exception as e:
            log.error(f"Failed to process caption command for {message.author}: {e}")
            await message.reply("Failed to process caption")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(Caption(bot))
        log.info("Caption cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load Caption cog: {e}")
        raise
