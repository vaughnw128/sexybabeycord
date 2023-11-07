# Sexybabeycord (A Sexybabeycord Production)

[![CI/CD](https://github.com/vaughnw128/sexybabeycord/actions/workflows/main.yml/badge.svg)](https://github.com/vaughnw128/sexybabeycord/actions/workflows/main.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

This is the newest iteration/amalgam of the many discord bots I've made over the years.
I plan on adding new bots and re-implementing old bots in this new and improved system!
The bot itself is a collection of multiple pieces, each with vastly
different functionalities. There certainly will be more to come as our
server never has enough bots (lie).

What the hell is Sexybabeycord?: Sexybabeycord is the current iteration of the Discord server that I share
with my close friends (we accidentally nuked the last one with homemade spambots). It's more of a
chaotic groupchat than a high-functioning Discord 'community,' as we all have Administrator
permissions, and we don't particularly care for rules. I love making bots for our server, and my
friends seem to as well.

## Simple Setup

Sexybabeycord uses poetry to manage most dependencies, so it should be fairly easy to set up on a new host.

### 1. Clone the repository
```bash
git clone https://github.com/vaughnw128/sexybabeycord
cd sexybabeycord/
```

### 2. Install and initialize pyenv

```bash
$ curl https://pyenv.run | bash
```

Add the following lines to ~/.bashrc and ~/.profile:
```bash
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Then, add the following like to ~/.bashrc to automatically initialize the virtual environment:
```bash
eval "$(pyenv virtualenv-init -)"
```

Finally, restart your shell and use pyenv to set the version. Currently, this version of Sexybabeycord uses Python 3.11.5.
```bash
$ pyenv install 3.11.5
$ pyenv local 3.11.5
```

### 3. Install poetry
```bash
$ curl -sSL https://install.python-poetry.org | python3 -
$ poetry self add poetry-dotenv-plugin
$ poetry install
```

### 4. Install final dependencies

MacOS:
```bash
$ brew install ffmpeg magickwand pre-commit
```

Unix:
```bash
$ apt get install ffmpeg libmagickwand-dev pre-commit
```

### 5. Set up your .env file
In order to pass in some of the variables for Sexybabeycord, the .env file should be set up.

Then, it's necessary to create a `.env` file to match the one in `bot/resources/templates/env_template` in the root directory of the project. The tenor token is required to grab certain gifs posted from tenor, and can be obtained for free by following the [Google Cloud Tenor Quickstart Guide](https://developers.google.com/tenor/guides/quickstart)

Additionally, some features require the use of a database, and some are supplemented by one. These features will be automatically disabled on startup of the bot if a database is not used. Finally, this bot is suited to only be used in a single guild at a time, therefore, the guild ID, general channel, and 'fate' channel must be passed in. If general or fate is not passed in, the corresponding features will not be available.

```bash
# TOKENS
DISCORD_TOKEN=
TENOR_TOKEN=

# DATABASE INFORMATION
MONGO_URI=
DATABASE_NAME=

# GUILD/CHANNEL INFORMATION
GUILD_ID=
GENERAL_CHANNEL_ID=
FATE_CHANNEL_ID=
```

### 6. Test feature functionality

Some cogs and utilities have build in unit tests. These features can be tested via pytest.

```bash
$ poetry run python -m pytest
```

### 7. Running the bot

Finally, once tests pass, the bot can be run

```bash
$ poetry run -m bot
```

## Dockerizing

Included with the bot is the ability to deploy it with Docker. The most recent image can be found under `packages` on Github. If you desire to build the container yourself, it can be easily built.

```bash
$ docker build .
```

Then to run the container:
```bash
$ docker run -d -ti --name sexybabeycord -v ./accounts.json:/bot/accounts.json -v ./.env:/bot/.env -v ./logs:/bot/logs --pull always ghcr.io/vaughnw128/sexybabeycord:latest
```

## Components

The current components (cogs) of the bot are as follows:
- Astropix: Scrapes and sends the NASA picture of the day every day at noon.
- Distort: Grabs images from messages then uses liquid rescaling to distort and resend them.
- fixlink: Takes any link to twitter, instagram, or tiktok, and fixes it with either the 'vx' or 'dd' prefix for proper embed formatting.
- fate: Uses twscrape to grab @JamesCageWhite's tweets and send them in our #fate channel. Love that guy.
- gabonganized: Gabonganizes all face pics sent. This adds a gabonga where someone's face is supposed to be.
- caption: Adds captions to images when you reply with the 'caption' keyword.
- Mood Meter: Allows users to select a coordinate from a drop down and then puts their profile photo on a mood matrix.
- Ytdl: Downloads youtube videos and clips with a command or menu button.
- Peanut gallery: Whenever someone sends a youtube link, a random comment from the video is automatically sent to chat
- Remind: Uses mongodb and crontab formatting to generate one-time reminders and recurring reminders
- Wrench: A small utility cog just for getting the JSON of a message


<sub><sup>Made with love and care by Vaughn Woerpel</sub></sup>
