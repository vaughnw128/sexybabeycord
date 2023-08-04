"""
    Constants

    Holds some constant values that need to be reused

    Made with love and care by Vaughn Woerpel
"""

# built-in
import os


class _Bot:
    prefix = "~"
    id = 873414777064542268
    token = os.getenv("DISCORD_TOKEN")
    tenor = os.getenv("TENOR_TOKEN")
    file_cache = "bot/resources/file_cache/"


Bot = _Bot()


class _Channels:
    yachts = 644752766736138241
    bots = 644753024287506452
    thots = 644753035993677831
    fate = 1021214119141064755


Channels = _Channels()


class _Guild:
    id = 644752766241341460


Guild = _Guild()


class _Logging:
    loglocation = "logs/"


Logging = _Logging()


class _Fate:
    accounts = "accounts.json"


Fate = _Fate()


class _Distort:
    ratio = 0.60


Distort = _Distort()


class _Caption:
    font = "bot/resources/caption_font.otf"


Caption = _Caption()
