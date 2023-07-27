import os

class _Bot():

    prefix = "~"
    id = 873414777064542268
    token = os.getenv("DISCORD_TOKEN")
    tenor = os.getenv("TENOR_TOKEN")

Bot = _Bot()


class _Channels():

    yachts = 644752766736138241
    bots = 644753024287506452
    thots = 644753035993677831
    fate = 1021214119141064755

Channels = _Channels()


class _Guild():

    id = 644752766241341460

Guild = _Guild()

class _Logging():

    logfile = "sexybabeycord.log"

Logging = _Logging()