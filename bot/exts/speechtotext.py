"""
    SpeechToText

    Allows users to right click voice messages and
    output them to the text channel

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os

# external
import discord
import speech_recognition as sr
from discord import app_commands
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
        self.speech_to_text_menu = app_commands.ContextMenu(
            name="Speech to text", callback=self.stt_menu
        )
        self.bot.tree.add_command(self.speech_to_text_menu)

    async def stt_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """Handles action of converting speech to text"""

        await interaction.response.defer()
        response = await speech_to_text_helper(message)

        match response:
            case "Message had no file":
                await interaction.followup.send("That message didn't have a file!!")
                return
            case "Not a voice message":
                await interaction.followup.send("Heh... that wasn't a voice message")
                return
            case "Unable to transcribe message":
                await interaction.followup.send(
                    "Erm, looks like I wasn't able to get that one..."
                )
                return

        await interaction.followup.send(content=response)


async def speech_to_text_helper(message: discord.Message) -> str:
    """Helper method for speech to text, also allows for testing"""

    fname = file_helper.grab(message)
    if fname is None:
        return "Message had no file"

    # Checks to see if it's a voice message
    if not fname.endswith("voice-message.ogg"):
        file_helper.remove(fname)
        return "Not a voice message"

    # Translates from ogg to wav
    wav_var = AudioSegment.from_ogg(fname)
    fname = fname.replace("ogg", "wav")
    wav_var.export(fname, format="wav")
    file_helper.remove(fname.replace("wav", "ogg"))

    # Recognizes the audio
    with sr.AudioFile(fname) as source:
        audio_text = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio_text)
            log.info(f"Voice message was transcribed {fname}")
            file_helper.remove(fname)
            return text
        except:
            log.warning(f"Voice message was unable to be transcribed {fname}")
            file_helper.remove(fname)
            return "Unable to transcribe message"


async def setup(bot: commands.Bot):
    """Sets up the cog

    Parameters
    -----------
    bot: commands.Bot
    The main cog runners commands.Bot object
    """

    # Adds the cog and reports that it's loaded
    await bot.add_cog(SpeechToText(bot))
    log.info("Loaded")
