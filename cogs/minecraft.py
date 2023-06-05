import discord
from discord.ext import tasks, commands
from discord import app_commands
from mcstatus import JavaServer

server = JavaServer.lookup("mc.sbcord.com")

class Minecraft(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="status")
    async def status(self, interaction: discord.Interaction):
        status = server.status()
        query = server.query()
        embed=discord.Embed(title="Minecraft Server Status", color=0x86f7a3)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/740341629323575338/1115069834930163843/server-icon.png")
        embed.add_field(name="Ping:", value=f"`{round(status.latency, 2)} ms`", inline=False)
        embed.add_field(name=f"Active Players ({status.players.online}/10):", value=f"{', '.join(query.players.names)}", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ip")
    async def ip(self, interaction: discord.Interaction):
        await interaction.response.send_message("The IP is `mc.sbcord.com` :3")

async def setup(bot: commands.Bot):
  """ Sets up the cog

     Parameters
     -----------
     bot: commands.Bot
        The main cog runners commands.Bot object
  """
  await bot.add_cog(Minecraft(bot))
  print("Minecraft: I'm loaded :]")

