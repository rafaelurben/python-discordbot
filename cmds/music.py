from discord.ext import commands
from discord import Embed, User, Member, opus, FFmpegPCMAudio, PCMVolumeTransformer, VoiceChannel
from fuzzywuzzy import process
import os, asyncio, youtube_dl

from . import serverfiles

filespath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "files")

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# opus.load_opus('opus')

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    'executable': os.path.join(filespath,"ffmpeg.exe")
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

#####

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xee00ff

    # sich in Entwicklung befindende Befehle

    if os.getenv("DEBUG", False):
        @commands.command(
            name='meme',
            brief='Spiele Memes',
            description='Spiele Memes von einer Audiodatei!',
            aliases=[],
            help="Benutze /meme <Name> um einen Meme abzuspielen.",
            usage="<Suche>"
        )
        @commands.guild_only()
        async def meme(self, ctx, search:str="schulgong.wav"):
            search = search+" "+ctx.getargs().rstrip("-l")
            filenames = list(os.listdir(os.path.join(str(filespath), "sounds")))

            result = process.extractOne(search, filenames)
            filename = result[0]

            print(search, result)

            if not (ctx.author.voice and ctx.author.voice.channel and ctx.author.voice.channel.guild == ctx.guild):
                raise commands.CommandError(message="Du musst dich in einem Sprachkanal befinden!")

            elif result[1] >= 75:
                audio = PCMVolumeTransformer(FFmpegPCMAudio(source=os.path.join(filespath, "sounds", filename), **ffmpeg_options))

                ctx.voice_client.play(audio, after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.sendEmbed(title="Spielt jetzt", color=self.color, fields=[("Meme",str(filename).split(".")[0])])
                #raise commands.BadArgument(message="Ich konnte die Audiodatei {} nicht abspielen.".format(filename))
            else:
                raise commands.BadArgument(message="Es wurden keine mit '{}' übereinstimmende Audiodatei gefunden.".format(search))

        @commands.command(
            name='memes',
            brief='Liste alle Memes auf',
            description='Liste alle Memes auf',
            aliases=[],
            help="Benutze /memes um eine Liste aller Memes zu erhalten.",
            usage=""
        )
        @commands.guild_only()
        async def memes(self, ctx):
            filenames = list(os.listdir(os.path.join(str(filespath), "sounds")))
            for chunk in list(chunks(filenames, 25)):
                fields = []
                for filename in chunk:
                    fields.append(("Meme", filename.split(".")[0]))
                await ctx.sendEmbed(title="Memes ("+str(len(chunk))+") - Gesamt: "+str(len(filenames)), color=self.color, fields=fields)

        # from example

        @commands.command(
            name='stop',
            brief='Stoppe Musik',
            description='Stoppe Musik!',
            aliases=["die","leave","disconnect"],
            help="Benutze /stop um den Bot aus dem Sprachkanal zu entfernen.",
            usage=""
        )
        @commands.guild_only()
        async def stop(self, ctx):
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            else:
                raise commands.BadArgument(message="Der Bot war in gar keinem Sprachkanal!")

        @commands.command(
            name='play',
            brief='Spiele Musik',
            description='Spiele Musik von Youtube und anderen Plattformen!',
            aliases=["yt","youtube","spotify"],
            help="Benutze /play <Url/Suche> um einen Song abzuspielen.",
            usage="<Url/Suche>"
        )
        async def play(self, ctx):
            url = ctx.getargs()
            async with ctx.typing():
                player = await YTDLSource.from_url(url.rstrip("-l"), loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

            await ctx.sendEmbed(title="Spielt jetzt", color=self.color, fields=[("Song", str(player.title))])

        @commands.command(
            name='stream',
            brief='Streame einen Stream',
            description='Streame einen Stream von Twitch oder YouTube',
            aliases=[],
            help="Benutze /stream <Url/Suche> den einen Stream zu streamen.",
            usage="<Url/Suche>"
        )
        async def stream(self, ctx):
            url = ctx.getargs()

            async with ctx.typing():
                player = await YTDLSource.from_url(url.rstrip("-l"), loop=self.bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

            await ctx.sendEmbed(title="Spielt jetzt", color=self.color, fields=[("Stream", str(player.title))])

        @commands.command(
            name='volume',
            brief='Ändere die Lautstärke',
            description='Ändere die Lautstärke des Bots',
            aliases=["lautstärke"],
            help="Benutze /volume <1-200> um die Lautstärke des Bots zu ändern.",
            usage="<1-200>"
        )
        async def volume(self, ctx, volume: int):
            if ctx.voice_client is None:
                raise commands.CommandError("Der Bot ist nicht mit einem Sprachkanal verbunden.")
            elif not ctx.voice_client.source:
                raise commands.CommandError("Der Bot scheint aktuell nichts abzuspielen.")

            old = ctx.voice_client.source.volume * 100
            ctx.voice_client.source.volume = volume / 100

            await ctx.sendEmbed(title="Lautstärke geändert", color=self.color, fields=[("Zuvor", str(old)+"%"),("Jetzt",str(volume)+"%")])


        @meme.before_invoke
        @play.before_invoke
        @stream.before_invoke
        async def autojoin(self, ctx):
            if ctx.author.voice:
                if ctx.voice_client is None:
                    await ctx.author.voice.channel.connect()
                elif ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    await ctx.voice_client.move_to(ctx.author.voice.channel)
                else:
                    await ctx.voice_client.move_to(ctx.author.voice.channel)
            else:
                raise commands.CommandError("Du bist mit keinem Sprachkanal verbunden!")

        @meme.after_invoke
        @play.after_invoke
        @stream.after_invoke
        async def autoleave(self, ctx):
            if "-l" in str(ctx.message.content):
                try:
                    while ctx.voice_client.is_playing():
                        await asyncio.sleep(0.2)
                    await ctx.voice_client.disconnect()
                except AttributeError:
                    pass



    # Generelle Commands

    @commands.command(
        name='usersong',
        brief='Stalke musikhörende Leute',
        description='Erhalte Links zu dem Song, welcher jemand gerade hört',
        aliases=[],
        help="Benutze /usersong <Member> um den Song zu erhalten",
        usage="<Member>"
    )
    @commands.guild_only()
    async def usersong(self, ctx, Member:Member):
        found = False
        for activity in Member.activities:
            if str(activity.type) == "ActivityType.listening":
                try:
                    await ctx.sendEmbed(title="User Song", color=self.color, fields=[("Titel", activity.title),("Künstler", activity.artist),("Link", ("[Spotify](https://open.spotify.com/track/"+activity.track_id+")"))])
                except AttributeError:
                    raise commands.BadArgument(message="Scheinbar hört dieser Benutzer keinen richtigen Song.")
                found = True
        if not found:
            raise commands.BadArgument(message="Dieser Benutzer hört keinen Song!")




def setup(bot):
    bot.add_cog(Music(bot))
