"""
SpeechToText

Allows users to right click voice messages and
output them to the text channel

Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
from io import BytesIO

# external
import discord
import speech_recognition as sr
from discord import app_commands
from discord.app_commands import errors as discord_errors
from discord.ext import commands
from pydub import AudioSegment

# project modules
from bot.utils import file_helper

recognizer = sr.Recognizer()
log = logging.getLogger("speech_to_text")


class SpeechToText(commands.Cog):
    """Speech to text cog for translating voice messages to text"""

    def __init__(self, bot: commands.Bot):
        """Initializes class with context menu"""

        self.bot = bot
        self.speech_to_text_menu = app_commands.ContextMenu(name="Speech to text", callback=self.stt_menu)
        self.bot.tree.add_command(self.speech_to_text_menu)

    async def stt_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Handles action of converting speech to text"""

        await interaction.response.defer()

        file, ext = await file_helper.grab_file(message)

        if ext != "ogg":
            raise discord_errors.AppCommandError("Hey, that's not a voice message!")

        # Translates from ogg to wav
        wav_var = AudioSegment.from_ogg(file)
        buf = BytesIO()
        wav_var.export(buf, format="wav")
        buf.seek(0)
        # Recognizes the audio
        with sr.AudioFile(buf) as source:
            audio_text = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio_text)
            except Exception:
                raise discord_errors.AppCommandError("Voice message was unable to be transcribed")
        await interaction.followup.send(text)


async def setup(bot: commands.Bot):
    """Sets up the cog."""
    await bot.add_cog(SpeechToText(bot))
    log.info("Loaded")
