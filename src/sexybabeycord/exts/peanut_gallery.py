"""Peanut Gallery

Automatically grabs a comment from whatever YouTube link is sent,
then sends it to chat

Made with love and care by Vaughn Woerpel
"""

# built-in
import asyncio
import io
import json
import logging
import random
import re
from contextlib import redirect_stdout
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

# external
import discord
from discord.ext import commands

log = logging.getLogger("peanut_gallery")

link_regex = r"https:\/\/(www.|)youtu(be.com|.be)([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"

executor = ThreadPoolExecutor(max_workers=2)


class PeanutGallery(commands.Cog):
    """PeanutGallery class to handle YouTube comment extraction"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize peanut_gallery"""
        self.bot = bot
        self._yt_dlp = None  # Lazy load yt-dlp
        log.info("PeanutGallery cog initialized")

    @property
    def yt_dlp(self):
        """Lazy load yt-dlp to avoid import overhead"""
        if self._yt_dlp is None:
            import yt_dlp
            self._yt_dlp = yt_dlp
        return self._yt_dlp

    def _extract_comments_sync(self, url: str) -> Optional[list]:
        """Synchronous comment extraction using optimized yt-dlp settings"""
        try:
            ydl_opts = {
                "extract_flat": "discard_in_playlist",
                "forcejson": True,
                "fragment_retries": 1,  # Minimal retries
                "getcomments": True,
                "ignoreerrors": "only_download",
                "noprogress": True,
                "quiet": True,
                "retries": 1,  # Minimal retries
                "simulate": True,
                "skip_download": True,
                "extractor_args": {"youtube": {"max_comments": ["25"]}},  # Reduced comments
                "socket_timeout": 5,  # Short timeout
                "http_chunk_size": 10485760,  # 10MB chunks for faster download
                "buffersize": 1024,  # Smaller buffer
                "nocheckcertificate": True,  # Skip SSL verification for speed
            }

            with io.StringIO() as buf, redirect_stdout(buf):
                with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download(url)
                    output = buf.getvalue()
            
            info = json.loads(output)
            return info.get("comments", [])
            
        except Exception as e:
            log.error(f"Failed to extract comments from {url}: {e}")
            return None

    async def _extract_comments_async(self, url: str) -> Optional[list]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self._extract_comments_sync, url)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Grab comment on link matching the regex"""
        if message.author.bot:
            return
            
        link_match = re.search(link_regex, message.content)
        if not link_match:
            return

        url = link_match.group(0)
        log.debug(f"Processing YouTube link: {url}")

        comments = await self._extract_comments_async(url)
        
        if not comments:
            log.debug("No comments found for YouTube video")
            return
            
        comment = random.choice(comments)
        log.debug(f"Selected comment from {comment.get('author', 'unknown')}")

        embed = discord.Embed(title="", description=comment["text"])
        embed.set_author(
            name=comment["author"],
            url=comment["author_url"],
            icon_url=comment["author_thumbnail"],
        )
        
        try:
            await message.reply(embed=embed)
            log.info(f"Successfully posted peanut gallery comment for {message.author}")
        except Exception as e:
            log.error(f"Failed to post peanut gallery comment for {message.author}: {e}")


async def setup(bot: commands.Bot) -> None:
    """Sets up the cog"""
    try:
        await bot.add_cog(PeanutGallery(bot))
        log.info("PeanutGallery cog loaded successfully")
    except Exception as e:
        log.error(f"Failed to load PeanutGallery cog: {e}")
        raise
