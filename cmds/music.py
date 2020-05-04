from discord.ext import commands
from discord import Embed, User, Member, opus, FFmpegPCMAudio
from fuzzywuzzy import process
import os

from . import serverfiles

filespath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "files")

# opus.load_opus('opus')

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
            help="Benutze /play <Name> um einen Meme abzuspielen.",
            usage="<Suche>"
        )
        @commands.guild_only()
        async def meme(self, ctx, search:str="schulgong.wav", *args):
            search = str(search+" "+" ".join(list(args)))
            filenames = list(os.listdir(os.path.join(str(filespath), "sounds")))

            result = process.extractOne(search, filenames)

            print(search,result)

            if not ctx.author.voice.channel:
                raise commands.BadArgument(message="Du musst dich in einem Sprachkanal befinden!")

            elif result[1] >= 65:
                filename = result[0]

                if ctx.guild.voice_client:
                    voice = ctx.guild.voice_client
                    await voice.move_to(ctx.author.voice.channel)
                    if voice.is_playing():
                        voice.stop()
                else:
                    voice = await ctx.author.voice.channel.connect()

                audio = FFmpegPCMAudio(source=os.path.join(filespath, "sounds", filename), executable=os.path.join(filespath,"ffmpeg.exe"))

                try:
                    voice.play(audio)
                except:
                    raise commands.BadArgument(message="Ich konnte die Audiodatei {} nicht abspielen.".format(filename))
            else:
                raise commands.BadArgument(message="Es wurde keine Audiodatei gefunden. Du hast nach {} gesucht.".format(search))

        @commands.command(
            name='memes',
            brief='Liste alle Memes auf',
            description='Liste alle Memes auf',
            aliases=[],
            help="Benutze /memes um eine Liste aller Memes zu erhalten.",
            usage=">"
        )
        @commands.guild_only()
        async def memes(self, ctx):
            filenames = list(os.listdir(os.path.join(str(filespath), "sounds")))
            EMBED = Embed(title="Memes ("+str(len(filenames))+")", color=self.color)
            EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            for filename in filenames:
                EMBED.add_field(name="Meme",value=filename.rstrip(".mp3").rstrip(".wav"),inline=True)
            await ctx.send(embed=EMBED)


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
            if ctx.guild.voice_client:
                await ctx.guild.voice_client.disconnect()
            else:
                raise commands.BadArgument(message="Der Bot war in gar keinem Sprachkanal!")




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
                    EMBED = Embed(title="User Song", color=self.color)
                    EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
                    EMBED.add_field(name="Titel",value=activity.title,inline=True)
                    EMBED.add_field(name="Künstler",value=activity.artist,inline=True)
                    EMBED.add_field(name="Link",value=("[Spotify](https://open.spotify.com/track/"+activity.track_id+")"),inline=False)
                    await ctx.send(embed=EMBED)
                except AttributeError:
                    raise commands.BadArgument(message="Scheinbar hört dieser Benutzer keinen richtigen Song.")
                found = True
        if not found:
            raise commands.BadArgument(message="Dieser Benutzer hört keinen Song!")




def setup(bot):
    bot.add_cog(Music(bot))
