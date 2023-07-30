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
            name="Speech to text", callback=self.speech_to_text
        )
        self.bot.tree.add_command(self.speech_to_text_menu)

    async def speech_to_text(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """Handles action of converting speech to text"""

        await interaction.response.defer(ephemeral=True)

        fname = file_helper.grab(message)

        if fname.endswith("voice-message.ogg"):
            wav_var = AudioSegment.from_ogg(fname)
            fname = fname.replace("ogg", "wav")
            wav_var.export(fname, format="wav")

            with sr.AudioFile(fname) as source:
                audio_text = recognizer.listen(source)
                try:
                    # using google speech recognition
                    text = recognizer.recognize_google(audio_text)
                    await message.reply(text)
                    await interaction.followup.send("Done!")
                    log.info(f"Voice message was transcribed {fname}")
                except:
                    await message.reply("Unable to transcribe message")
                    await interaction.followup.send("Done!")
                    log.warning(f"Voice message was unable to be transcribed {fname}")
            os.remove(fname)
            os.remove(fname.replace("wav", "ogg"))
        else:
            await interaction.followup.send("Not a voice message.")


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
