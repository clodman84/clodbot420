import youtube_dl as ytdl
from discord import Embed, FFmpegPCMAudio, PCMVolumeTransformer
from commands import bot
import asyncio
from discord import ClientException
from typing import List
import spotify

# RIP GROOVY.

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist",
}

FFMPEG_BEFORE_OPTS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"


class MusiCUNT:
    cunts = []

    def __init__(self, client, channel):
        self.current_song = None
        self.playlist: List[Song] = []
        self.client = client
        self.channel = channel
        self.now_playing = None
        # gets appended to the list of clients
        MusiCUNT.cunts.append(self)

    def next_song(self, err):
        asyncio.run_coroutine_threadsafe(self.now_playing.delete(), bot.loop)
        if len(self.playlist) > 0:
            next_song = self.playlist.pop(0)
            asyncio.run_coroutine_threadsafe(self.play_song(next_song), bot.loop)
        else:
            asyncio.run_coroutine_threadsafe(self.die(), bot.loop)

    def add_song(self, song):
        self.playlist.extend(song)

    async def play_song(self, song):
        self.current_song = song
        source = PCMVolumeTransformer(
            FFmpegPCMAudio(await song.stream_url, before_options=FFMPEG_BEFORE_OPTS)
        )
        self.now_playing = await self.channel.send(embed=song.get_embed())
        self.client.play(source, after=self.next_song)

    def pause(self):
        if self.client.is_playing():
            self.client.pause()
        else:
            self.client.resume()

    async def die(self):
        MusiCUNT.cunts.remove(self)
        await self.client.disconnect()
        # all references should be gone, garbage collected

    def __str__(self):
        return f"playlist:{[str(song) for song in self.playlist]}, {self.client}"


class Song:
    """Song objects"""

    def __init__(self, query):
        info = Song.get_info(query=query)
        self.title = info["title"]
        self.duration = info["duration"]
        self.page_url = info["webpage_url"]

    @property
    async def stream_url(self):
        info = await bot.loop.run_in_executor(None, self.get_info, self.page_url)
        return info["url"]

    @staticmethod
    def get_info(query):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(query, download=False)
            if "_type" in info and info["_type"] == "playlist":
                info = Song.get_info(info["entries"][0]["url"])
        return info

    def get_embed(self):
        return Embed(title=self.title, url=self.page_url, color=0x1ED9C0)

    def __str__(self):
        return "title : {}, url : {}, duration : {}, page_url = {}".format(
            self.title, self.stream_url, self.duration, self.page_url
        )


async def process_query(query):
    if "spotify" in query:
        data = await spotify.getPlaylist(query)
        song_task = []
        for i in data["songs"]:
            song = bot.loop.run_in_executor(None, Song, i)
            song_task.append(song)
        song_list = await asyncio.gather(*song_task)
        return song_list, data["image"]
    else:
        # if it is not a spotify link then it is a YouTube link, download error should catch the any other link
        return [
            Song(query=query)
        ], False  # returns a list for compatibility with Spotify playlists


@bot.command()
async def play(ctx, *args):
    # detect which channel to join and then join
    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel
    else:
        await ctx.send("You need to be in a voice channel to use this command.")
        return
    player = False

    try:
        song = await process_query(" ".join(args[:]))
        image = song[1]
        song = song[0]
    except ytdl.DownloadError as e:
        await ctx.send(f"There was an error : {e}")
        return

    for musi_cunt in MusiCUNT.cunts:
        # searches through the list of clients
        if musi_cunt.client.is_playing() and musi_cunt.client.channel == voice_channel:
            # append to the clients list of songs of the musiCUNT if it is already playing a song and in the same
            # channel as the person who invoked the bot
            player = musi_cunt
            player.add_song(song)
            embed = Embed(
                title=f'{len(song)} {"item" if len(song) == 1 else "items"} added to '
                f"queue!",
                color=0x1ED9C0,
            )
            if image:
                embed.set_image(url=image)
            await ctx.send(embed=embed, delete_after=15)

    if not player:
        try:
            client = await voice_channel.connect()
        except ClientException as e:
            await ctx.send(f"There was an error {e}")
            return

        player = MusiCUNT(client, channel=ctx.channel)
        player.add_song(song[1:])
        await player.play_song(song[0])
        embed = Embed(
            title="The King is dead, long live the King!", color=0x1ED9C0
        ).set_footer(text="RIP Groovy")
        if image:
            embed.set_image(url=image)

        await ctx.send(embed=embed)


@bot.command()
async def pause(ctx):
    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel
    else:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    for musi_cunt in MusiCUNT.cunts:
        if musi_cunt.client.channel == voice_channel:
            musi_cunt.pause()
            return


@bot.command()
async def disconnect(ctx):
    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel
    else:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    musi_cunt: MusiCUNT
    for musi_cunt in MusiCUNT.cunts:
        if musi_cunt.client.channel == voice_channel:
            musi_cunt.playlist.clear()
            musi_cunt.client.stop()
            await ctx.send("Sayonara Cocksucker!")
            return


@bot.command()
async def skip(ctx):
    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel
    else:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    musi_cunt: MusiCUNT
    for musi_cunt in MusiCUNT.cunts:
        if musi_cunt.client.channel == voice_channel:
            musi_cunt.client.stop()
            return
