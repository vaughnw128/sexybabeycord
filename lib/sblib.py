import validators
import discord
import requests
import urllib
import os

TENOR_TOKEN = os.getenv("TENOR_TOKEN")

async def grab_file(message: discord.Message):
    types = ["png", "jpg", "jpeg", "gif", "mp4"]
    url = None
    # Finds the URL that the image is at
    if message.embeds:
        # Checks if the embed itself is an image and grabs the url
        if message.embeds[0].thumbnail.proxy_url is not None:
            url = message.embeds[0].thumbnail.proxy_url
        elif message.embeds[0].url is not None:
            url = message.embeds[0].url
        elif message.embeds[0].video.url is not None:
            url = message.embeds[0].video.url

        
    # Checks to see if the image is a message attachment
    elif message.attachments:
        url = message.attachments[0].url

    else:
        for item in message.content.split(" "):
            if validators.url(item):
                url = item

    if url is None:
        return None
    
    # Remove the trailing modifiers at the end of the link
    url = url.partition("?")[0]

    if "tenor" in url:
        id = url.split("-")[len(url.split("-")) - 1]
        resp = requests.get(
            f"https://tenor.googleapis.com/v2/posts?key={TENOR_TOKEN}&ids={id}&limit=1"
        )
        data = resp.json()
        url = data["results"][0]["media_formats"]["mediumgif"]["url"]

    if not url.endswith(tuple(types)):
        print("not url")
        return None
    
    if validators.url(url):
        fname = requests.utils.urlparse(url)
        fname = f"images/{os.path.basename(fname.path)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with open(fname, "wb") as f:
            with urllib.request.urlopen(req) as r:
                f.write(r.read())
    return fname