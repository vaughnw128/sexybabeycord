"""SpeechToText

Allows users to right click voice messages and
output them to the text channel

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
from io import BytesIO
from typing import Optional

# external
import discord
import speech_recognition as sr
from discord import app_commands
from discord.app_commands import errors as discord_errors
from discord.ext import commands
from pydub import AudioSegment

# project modules
from sexybabeycord.utils import file_helper

recognizer = sr.Recognizer()
log = logging.getLogger("speech_to_text")


class SpeechToText(commands.Cog):
    """Speech to text cog for translating voice messages to text"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes class with context menu"""
        self.bot = bot
        self.speech_to_text_menu = app_commands.ContextMenu(name="speech to text", callback=self.stt_menu)
        self.bot.tree.add_command(self.speech_to_text_menu)
        log.info("SpeechToText cog initialized")

    async def stt_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Handles action of converting speech to text"""
        log.debug(f"Speech-to-text request from {interaction.user} for message {message.id}")
        await interaction.response.defer()

        try:
            file, ext = await file_helper.grab_file(message)
            log.debug(f"Retrieved file with extension: {ext}")

            if ext != "ogg":
                log.warning(f"Invalid file type for speech-to-text: {ext}")
                raise discord_errors.AppCommandError("Hey, that's not a voice message!")

            # Lazy load speech recognition libraries only when needed
            try:
                import speech_recognition as sr
                from pydub import AudioSegment
            except ImportError:
                log.error("Speech recognition libraries not available")
                await interaction.followup.send("Speech recognition libraries not available")
                return

            # Initialize recognizer
            recognizer = sr.Recognizer()

            # Translates from ogg to wav
            wav_var = AudioSegment.from_ogg(file)
            buf = BytesIO()
            wav_var.export(buf, format="wav")
            buf.seek(0)
            log.debug("Successfully converted audio to WAV format")

            # Recognizes the audio
            with sr.AudioFile(buf) as source:
                audio_text = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio_text)
                    log.info(f"Successfully transcribed audio for user {interaction.user}")
                    await interaction.followup.send(text)
                except Exception as e:
                    log.error(f"Failed to transcribe audio: {e}")
                    raise discord_errors.AppCommandError("Voice message was unable to be transcribed")
                    
        except Exception as e:
            log.error(f"Speech-to-text processing failed: {e}")
            raise


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog."""
    try:
        await bot.add_cog(SpeechToText(bot))
        log.info("SpeechToText cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load SpeechToText cog: {e}")
        raise
