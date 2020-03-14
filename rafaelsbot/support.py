from discord.ext import commands
from discord import Embed, Member, User
from . import serverfiles
import time

class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xffdf00

    @commands.command(
        brief='Melde einen Spieler',
        description='Benutze diesen Command um Spieler zu melden',
        aliases=[],
        help="Wenn ein Benutzer Blödsinn treibt, dann benutze /report <Member> [Grund]",
        usage="<Member> [Grund]"
        )
    async def report(self, ctx, Member: Member, *args):
        Grund = " ".join(args)
        serverfiles.createReport(ctx.guild.id,Member.id,Grund,ctx.author.id)
        EMBED = Embed(title="Benutzer Gemeldet", color=self.color)
        EMBED.set_footer(text=f'Auftraggeber: {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        EMBED.add_field(name="Betroffener",value=Member.mention)
        EMBED.add_field(name="Grund",value=Grund)
        await ctx.send(embed=EMBED)
        return


    @commands.command(
        brief='Erhalte alle Reports',
        description='Benutze diesen Command um alle Reports zu sehen',
        aliases=["getreports","getreport"],
        help="Mit /getreports [Member] kannst du alle Reports ansehen.",
        usage="[Member]"
        )
    @commands.has_any_role("Moderator","Supporter","Admin")
    async def reports(self, ctx, Member:Member=None):
        if Member == None:
            EMBED = Embed(title="Server Reports", color=self.color)
            EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            for user in serverfiles.getReports(ctx.guild.id):
                EMBED.add_field(name=str(user[1])+" Report(s)",value="<@"+str(user[0])+">",inline=False)
            await ctx.send(embed=EMBED)
        else:
            EMBED = Embed(title="User Reports", color=self.color, description=("User: "+Member.mention))
            EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            for report in serverfiles.getReports(ctx.guild.id,Member.id):
                EMBED.add_field(name=str(time.strftime('%d.%m.%Y - %H:%M:%S', time.localtime(report["timestamp"]))),value=str(report["reason"])+" - <@"+str(report["reportedbyid"])+">",inline=False)
            await ctx.send(embed=EMBED)
        return




def setup(bot):
    bot.add_cog(Support(bot))
