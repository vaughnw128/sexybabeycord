# Sexybabeycord (A Sexybabeycord Production)

[![Build](https://github.com/vaughnw128/sexybabeycord/actions/workflows/build.yml/badge.svg)](https://github.com/vaughnw128/sexybabeycord/actions/workflows/main.yml)
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

Special thanks to [@CowZix](https://github.com/CowZix) for creating the `asher` cog. He is a truly elite contributor.

## Prerequisites

Before setting up Sexybabeycord, make sure you have the following installed:

- **Python 3.12**
- **uv**
- **FFmpeg** 
- **ImageMagick**

## Quick Setup

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the repository

```bash
git clone https://github.com/vaughnw128/sexybabeycord
cd sexybabeycord/
```

### 3. Install dependencies

Sexybabeycord uses uv to manage dependencies. Install them with:

```bash
uv sync
```

### 4. Install system dependencies

```bash
sudo apt update
sudo apt install ffmpeg libmagickwand-dev
```

### 5. Set up environment variables

Create a `.env` file in the project root with the following variables:

```bash
# REQUIRED: Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# REQUIRED: Tenor API Token (for GIF functionality)
TENOR_TOKEN=your_tenor_token_here

# REQUIRED: Guild/Server Information
GUILD_ID=your_guild_id_here
GENERAL_CHANNEL_ID=your_general_channel_id_here

# OPTIONAL: Database Configuration (MongoDB)
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=sexybabeycord

# OPTIONAL: Fate Channel (for Twitter integration)
FATE_CHANNEL_ID=your_fate_channel_id_here
```

#### Getting the required tokens:

1. **Discord Bot Token**: 
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section
   - Copy the token

2. **Tenor Token**: 
   - Follow the [Google Cloud Tenor Quickstart Guide](https://developers.google.com/tenor/guides/quickstart)
   - It's free and only requires a Google Cloud account

3. **Guild and Channel IDs**: 
   - Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
   - Right-click on your server and channels to copy their IDs

### 6. Test the installation

Run the test suite to ensure everything is working:

```bash
uv run pytest
```

### 7. Run the bot

Start the bot with:

```bash
uv run sexybabeycord
```

Or run the module directly:

```bash
uv run python -m sexybabeycord
```

## Development Setup

For development work, install the additional development dependencies:

```bash
uv sync --group dev
```

### Code Quality Tools

The project uses several tools for code quality:

- **ruff**: Fast Python linter and formatter
- **pre-commit**: Git hooks for code quality
- **pytest**: Testing framework

Run the linter:
```bash
uv run ruff check .
```

Format code:
```bash
uv run ruff format .
```

Run tests:
```bash
uv run pytest
```

## Docker Deployment

### Quick Start with Docker

The easiest way to run Sexybabeycord is using the pre-built Docker image:

```bash
docker run -d \
  --name sexybabeycord \
  -e DISCORD_TOKEN=your_token \
  -e TENOR_TOKEN=your_tenor_token \
  -e GUILD_ID=your_guild_id \
  -e GENERAL_CHANNEL_ID=your_channel_id \
  --restart always \
  ghcr.io/vaughnw128/sexybabeycord:latest
```

### Building from Source

If you want to build the Docker image yourself:

```bash
docker build -t sexybabeycord .
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  sexybabeycord:
    image: ghcr.io/vaughnw128/sexybabeycord:latest
    container_name: sexybabeycord
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - TENOR_TOKEN=${TENOR_TOKEN}
      - GUILD_ID=${GUILD_ID}
      - GENERAL_CHANNEL_ID=${GENERAL_CHANNEL_ID}
      - MONGO_URI=${MONGO_URI}
      - DATABASE_NAME=${DATABASE_NAME}
      - FATE_CHANNEL_ID=${FATE_CHANNEL_ID}
    restart: always
    volumes:
      - sexybabeycord_data:/bot/data
```

Then run:
```bash
docker-compose up -d
```

## Bot Features

### Current Components (Cogs)

- **Caption**: Adds captions to images when you reply with the 'caption' keyword
- **Distort**: Grabs images from messages and uses liquid rescaling to distort them
- **FixLink**: Automatically fixes Twitter, Instagram, and TikTok links for proper embed formatting
- **Fate**: Uses twscrape to grab @JamesCageWhite's tweets and send them in the #fate channel
- **MoodMeter**: Allows users to select coordinates from dropdown menus and places their profile photo on a mood matrix
- **SpeechToText**: Converts voice messages to text via right-click context menu
- **Asher**: Makes Asher present on images via right-click context menu
- **Mogged**: Reacts with emojis when certain keywords are detected
- **Gabonganized**: Adds a gabonga where someone's face is supposed to be
- **Peanut Gallery**: Sends random comments from YouTube videos when links are shared

### Archived Components

- **Wrench**: Utility cog for getting JSON of messages
- **Astropix**: Scrapes and sends NASA picture of the day daily at noon
- **Ytdl**: Downloads YouTube videos and clips with commands or menu buttons
- **Remind**: Uses MongoDB and crontab formatting for one-time and recurring reminders

## Contributing

I'm absolutely happy to have any contributions to this project, and please feel free to open a pull request!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<sub><sup>Made with love and care by Vaughn Woerpel</sub></sup>
