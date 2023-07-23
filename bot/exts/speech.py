import os
import random
import urllib

import discord
import speech_recognition as sr
from discord import app_commands
from discord.ext import commands
from pydub import AudioSegment

recognizer = sr.Recognizer()


class SpeechToText(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.speech_to_text_menu = app_commands.ContextMenu(
            name="Speech to text", callback=self.speech_to_text
        )
        self.bot.tree.add_command(self.speech_to_text_menu)

    async def speech_to_text(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.defer(ephemeral=True)

        url = str(message.attachments[0])
        if "voice-message.ogg" in url:
            fname = url.split("/")
            fname = "bot/resources/audio/" + fname[len(fname) - 1]
            fname = fname.split(".")[0] + str(random.randint(0, 10000)) + ".ogg"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with open(fname, "wb") as f:
                with urllib.request.urlopen(req) as r:
                    f.write(r.read())

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
                except:
                    await message.reply("Unable to transcribe message")
                    await interaction.followup.send("Done!")
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

    if not os.path.exists("bot/resources/audio"):
        os.makedirs("bot/resources/audio")

    # Adds the cog and reports that it's loaded
    await bot.add_cog(SpeechToText(bot))
    print("SpeechToText: I'm loaded 🚀")
