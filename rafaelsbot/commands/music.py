from discord.ext import commands
from discord import Embed, User, Member
from . import serverfiles

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xee00ff

    @commands.command(
        name='play',
        brief='Spiele Musik',
        description='Spiele Musik von YouTube!',
        aliases=["yt","youtube"],
        help="Benutze /play <Link> um ein YouTube Video abzuspielen",
        usage="<Link>"
    )
    async def play(self, ctx):
        pass


    @commands.command(
        name='usersong',
        brief='Stalke musikhörende Leute',
        description='Erhalte Links zu dem Song, welcher jemand gerade hört',
        aliases=[],
        help="Benutze /usersong <Member> um den Song zu erhalten",
        usage="<Member>"
    )
    async def usersong(self, ctx, Member:Member):
        found = False
        for activity in Member.activities:
            if str(activity.type) == "ActivityType.listening":
                EMBED = Embed(title="User Song", color=self.color)
                EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
                EMBED.add_field(name="Titel",value=activity.title,inline=True)
                EMBED.add_field(name="Künstler",value=activity.artist,inline=True)
                EMBED.add_field(name="Link",value=("[Spotify](https://open.spotify.com/track/"+activity.track_id+")"),inline=False)
                await ctx.send(embed=EMBED)
                found = True
        if not found:
            raise commands.BadArgument(message="Dieser Benutzer hört keinen Song!")




def setup(bot):
    bot.add_cog(Music(bot))
