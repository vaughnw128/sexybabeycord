"""
    Constants

    Holds some constant values that need to be reused

    Made with love and care by Vaughn Woerpel
"""

# built-in
import os
from dotenv import load_dotenv
load_dotenv()

from dotenv import load_dotenv

load_dotenv()


class _Bot:
    prefix = "~"
    token = os.getenv("DISCORD_TOKEN")
    tenor = os.getenv("TENOR_TOKEN")
    file_cache = "bot/resources/file_cache/"

    if token is None or token == "":
        raise ValueError("DISCORD_TOKEN is not set.")
    if tenor is None or tenor == "":
        raise ValueError("TENOR_TOKEN is not set.")


Bot = _Bot()


class _Database:
    connection_uri = os.getenv("MONGO_URI")
    database = os.getenv("DATABASE_NAME")

Database = _Database()

class _Channels:
    general = os.getenv("GENERAL_CHANNEL_ID")
    fate = os.getenv("FATE_CHANNEL_ID")

    if general is None or general == "":
        raise ValueError("TENOR_TOKEN is not set.")

Channels = _Channels()


class _Guild:
    id = os.getenv("GUILD_ID")

    if id is None or id == "":
        raise ValueError("GUILD_ID is not set.")


Guild = _Guild()


class _Logging:
    loglocation = "logs/"


Logging = _Logging()


class _Fate:
    accounts = "data/accounts.json"


Fate = _Fate()


class _Distort:
    ratio = 0.60


Distort = _Distort()


class _Caption:
    fontdir = "bot/resources/fonts/"
    fonts = {
        "default": f"{fontdir}ifunny.otf",
        "sans": f"{fontdir}sans.ttf",
        "papyrus": f"{fontdir}papyrus.ttf",
        "viz": f"{fontdir}WhizBangRoman.ttf",
    }


Caption = _Caption()


class _MoodMeter:
    image = "bot/resources/MoodMeter.png"

    number_emojis = (
        "0️⃣",
        "1️⃣",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
        "9️⃣",
    )
    letter_emojis = ("🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯")

    location = {
        "9": 224,
        "8": 311,
        "7": 398,
        "6": 485,
        "5": 572,
        "4": 659,
        "3": 746,
        "2": 833,
        "1": 920,
        "0": 1007,
        "A": 242,
        "B": 329,
        "C": 416,
        "D": 503,
        "E": 590,
        "F": 677,
        "G": 764,
        "H": 851,
        "I": 938,
        "J": 1025,
    }


MoodMeter = _MoodMeter()
