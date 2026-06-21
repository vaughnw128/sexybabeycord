# built-in
import logging
import random
import re
import unicodedata

# external
import discord
from discord.ext import commands

log = logging.getLogger("goke")

correction_message = "Hey there! It looks like you mentioned 'gloke' in some form. I think you meant GOKE!"
goke_regex = re.compile(r"\bgoke\b", re.IGNORECASE)
goke_reactions = ("🇬", "🇴", "🇰", "🇪")
epithets = (
    "Goke will cleanse us all with his holy light!",
    "Glory to goke!",
    "Hail goke!",
    "All heretics shall be purged in the name of goke!",
    "Bow before goke's glory!",
    "Goke will save us all!",
    "Goke is the one true god!",
    "Goke's light will guide us!",
    "Goke will protect us from the darkness!",
)

character_filters = str.maketrans(
    {
        "0": "o",
        "1": "l",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
        "i": "l",
        "¡": "i",
        "ı": "l",
        "і": "l",
        "ɩ": "l",
        "ⅼ": "l",
        "ℓ": "l",
        "λ": "l",
        "ӏ": "l",
        "|": "l",
        "!": "l",
        "ø": "o",
        "ö": "o",
        "ó": "o",
        "ò": "o",
        "ô": "o",
        "õ": "o",
        "ō": "o",
        "ο": "o",
        "о": "o",
        "Օ": "o",
        "ｅ": "e",
        "е": "e",
        "ё": "e",
        "є": "e",
        "℮": "e",
        "ɡ": "g",
        "ց": "g",
        "ǵ": "g",
        "ğ": "g",
        "ǧ": "g",
        "ｋ": "k",
        "κ": "k",
        "к": "k",
    }
)

filtered_keywords = frozenset(
    {
        "gloke",
        "gloake",
        "gloak",
        "glouke",
        "glowke",
        "gloque",
        "glokie",
        "gloky",
        "golke",
        "golk",
    }
)


class Goke(commands.Cog):
    """Deletes gloke messages and sends the author a correction."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Goke cog."""

        self.bot = bot
        log.info("Goke cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Correct messages containing the word gloke."""

        if message.author.bot:
            return

        if contains_filtered_gloke(message.content):
            await correct_gloke_message(message)
            return

        if contains_goke_word(message.content):
            await react_to_goke_message(message)


async def correct_gloke_message(message: discord.Message) -> None:
    """Delete gloke messages and send the author a correction."""

    log.debug(f"Gloke keyword detected from {message.author}")

    try:
        await message.delete()
        log.info(f"Deleted gloke message from {message.author}")
    except Exception as e:
        log.error(f"Failed to delete gloke message from {message.author}: {e}")
        return

    try:
        await message.author.send(correction_message + " " + random.choice(epithets))
        log.debug(f"Sent goke correction to {message.author}")
    except discord.Forbidden:
        await message.channel.send(f"{message.author.mention} {correction_message}", delete_after=30)
        log.debug(f"Sent fallback goke correction to {message.author}")
    except Exception as e:
        log.error(f"Failed to send goke correction to {message.author}: {e}")


async def react_to_goke_message(message: discord.Message) -> None:
    """React to messages that contain the word goke."""
    log.debug(f"Goke keyword detected from {message.author}")

    try:
        for reaction in goke_reactions:
            await message.add_reaction(reaction)
        log.debug(f"Added goke reactions to message from {message.author}")
    except Exception as e:
        log.error(f"Failed to add goke reactions: {e}")


def normalize_filter_text(content: str) -> str:
    content = content.replace("||", "")
    normalized = unicodedata.normalize("NFKC", content).casefold().translate(character_filters)
    filtered_characters = []

    for character in normalized:
        category = unicodedata.category(character)
        if category[0] in {"C", "M"}:
            continue
        if not character.isalnum():
            continue
        filtered_characters.append(character)

    return "".join(filtered_characters)


def contains_filtered_gloke(content: str) -> bool:
    normalized = normalize_filter_text(content)
    return any(keyword in normalized for keyword in filtered_keywords)


def contains_goke_word(content: str) -> bool:
    return goke_regex.search(content) is not None


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog."""

    try:
        await bot.add_cog(Goke(bot))
        log.info("Goke cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load Goke cog: {e}")
        raise
