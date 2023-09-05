"""
    Bash

    Allows users to do cursed things

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import subprocess

# external
import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("bash")


class Bash(commands.Cog):
    """Bash class to handle all your insecurities"""

    def __init__(self, bot: commands.Bot) -> None:
        """Intializes the bash class"""

        # subprocess.run("docker run -dit --name alpine alpine", shell=True)

        self.bot = bot

    @app_commands.command(name="bash")
    async def bash(self, interaction: discord.Interaction, command: str) -> None:
        await interaction.response.defer()

        # command = ["docker", "exec", "alpine"] + command.split(" ")

        output = exec()
        output = [line.decode() for line in output if line is not None]
        printable = "".join(output)

        if len(printable) == 0:
            await interaction.followup.send("erm... that didn't work!")
            return

        await interaction.followup.send(f"```{printable}```")


def exec(cmd: str) -> tuple:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        return proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        return proc.communicate()


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""

    await bot.add_cog(Bash(bot))
    log.info("Loaded")
