import discord
from discord import app_commands
from discord.ext import commands

class Statcat(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @commands.Cog.listener("on_message")
    async def get_message(self, message):
        print(message)


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Statcat(bot))
  print("Cog - Statcat Loaded!")