"""
    Constants

    Holds some constant values that need to be reused

    Made with love and care by Vaughn Woerpel
"""

# built-in
import os


class _Bot:
    prefix = "~"
    testing = True
    if testing:
        token = os.getenv("TESTING_TOKEN")
        id = 1137764471725625354
    else:
        token = os.getenv("DISCORD_TOKEN")
        id = 873414777064542268
    tenor = os.getenv("TENOR_TOKEN")
    file_cache = "bot/resources/file_cache/"


Bot = _Bot()


class _Channels:
    if Bot.testing:
        yachts = 1137763756869427231
        bots = 1137763767963357184
        thots = 1137763783037685820
        fate = 1137763793364074556
    else:
        yachts = 644752766736138241
        bots = 644753024287506452
        thots = 644753035993677831
        fate = 1021214119141064755


Channels = _Channels()


class _Guild:
    if Bot.testing:
        id = 740341628694298778
    else:
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
