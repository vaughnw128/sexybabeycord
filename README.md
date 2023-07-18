# Sexybabeycord (A Sexybabeycord Production)

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

## Usage

dlib is now required due to face_recognition in the gabonganizer.

```
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build; cd build; cmake ..; cmake --build .
```

This bot now uses poetry to manage dependencies, and can therefore be run with `poetry run python sexybabeycord.py`. No dependencies have to be installed, as the virtual environment will handle it. Environment variables will need to be supplied in a .env file.

Installing dependencies with poetry:
```
poetry env use 3.10.6
poetry self add poetry-dotenv-plugin
poetry install
```

## Components

The current components (cogs) of the bot are as follows:
- Astropix: Scrapes and sends the NASA picture of the day every day at noon.
- Statcat: Message statistics generator.
- Distort: Grabs images from messages then uses liquid rescaling to distort and resend them.
- fixlink: Takes any link to twitter, instagram, or tiktok, and fixes it with either the 'vx' or 'dd' prefix for proper embed formatting.
- fate: Uses twscrape to grab @JamesCageWhite's tweets and send them in our #fate channel. Love that guy.
- gabonganized: Gabonganizes all face pics sent. This adds a gabonga where someone's face is supposed to be.

Components that I plan on adding in the future:
- Not sure!
    
    
<sub><sup>Made with love and care by Vaughn Woerpel</sub></sup>
