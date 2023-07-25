import os
from enum import Enum

class EnvConfig():
    """Our default configuration for models that should load from .env files."""

    class Config:
        """Specify what .env files to load, and how to load them."""

        env_file = ".env",
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


class _Bot(EnvConfig):
    EnvConfig.Config.env_prefix = "bot_"

    prefix = "~"
    id = 873414777064542268
    token = os.getenv("DISCORD_TOKEN")
    tenor = os.getenv("TENOR_TOKEN")

Bot = _Bot()


class _Channels(EnvConfig):
    EnvConfig.Config.env_prefix = "channels_"

    yachts = 644752766736138241
    bots = 644753024287506452
    thots = 644753035993677831
    fate = 1021214119141064755

Channels = _Channels()


class _Guild(EnvConfig):
    EnvConfig.Config.env_prefix = "guild_"

    id = 644752766241341460

Guild = _Guild()