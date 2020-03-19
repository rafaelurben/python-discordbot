from discord.ext import commands
from discord import Embed, Member, User, Permissions


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x5156ff

    @commands.command(
        brief="Leert den Chat",
        description="Leert den Chat",
        aliases=["cc"],
        help="Gib einfach /clearchat ein und der Chat wird bald leer sein",
        usage=""
        )
    @commands.has_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages = True)
    async def clearchat(self,ctx):
        await ctx.message.channel.purge()
        return



    @commands.command(
        brief="Kickt einen Spieler",
        description="Kickt einen Spieler vom Server",
        aliases=[],
        help="Benutze /kick <Member> [Grund] um einen Spieler zu kicken",
        usage="<Member> [Grund]"
        )
    @commands.has_permissions(kick_members = True)
    @commands.bot_has_permissions(kick_members = True)
    async def kick(self, ctx, Member: Member, *args):
        Grund = " ".join(args)
        if Grund.rstrip() == "":
            Grund = "Leer"
        EMBED = Embed(title="Benutzer Gekickt", color=self.color)
        EMBED.set_footer(text=f'Auftraggeber: {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        EMBED.add_field(name="Betroffener",value=Member.mention)
        EMBED.add_field(name="Grund",value=Grund)
        await Member.kick(reason=Grund)
        await ctx.send(embed=EMBED)
        return


    @commands.command(
        brief="Bannt einen Spieler",
        description="Bannt einen Spieler vom Server",
        aliases=[],
        help="Benutze /ban <Member> [Grund] um einen Spieler zu bannen",
        usage="<Member> [Grund]"
        )
    @commands.has_permissions(ban_members = True)
    @commands.bot_has_permissions(ban_members = True)
    async def ban(self, ctx, Member: Member, *args):
        Grund = " ".join(args)
        if Grund.rstrip() == "":
            Grund = "Leer"
        EMBED = Embed(title="Benutzer Gebannt", color=self.color)
        EMBED.set_footer(text=f'Auftraggeber: {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        EMBED.add_field(name="Betroffener",value=Member.mention)
        EMBED.add_field(name="Grund",value=Grund)
        await Member.kick(reason=Grund)
        await ctx.send(embed=EMBED)
        return



    @commands.command(
        brief="Entbannt einen Spieler",
        description="Entbannt einen zuvor gebannten Spieler",
        aliases=["pardon"],
        help="Benutze /unban <Userid> [Grund] um einen Spieler zu entbannen",
        usage="<Userid> [Grund]"
        )
    @commands.has_permissions(ban_members = True)
    @commands.bot_has_permissions(ban_members = True)
    async def unban(self, ctx, userid: int, *args):
        Grund = " ".join(args)
        if Grund.rstrip() == "":
            Grund = "Leer"
        User = self.bot.get_user(userid)
        if User == None:
            raise commands.BadArgument(message="Benutzer wurde nicht gefunden!")
        EMBED = Embed(title="Benutzer Entbannt", color=self.color)
        EMBED.set_footer(text=f'Auftraggeber: {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        EMBED.add_field(name="Betroffener",value=User.mention)
        EMBED.add_field(name="Grund",value=Grund)
        try:
            await ctx.guild.unban(User,reason=Grund)
            await ctx.send(embed=EMBED)
        except:
            raise commands.BadArgument(message="Benutzer wurde nicht gefunden!")
        return


    @commands.command(
        brief="Tötet einen Spieler",
        description="Kickt einen Spieler aus dem aktuellen Sprachkanal",
        aliases=["kickvoice"],
        help="Benutze /kill <Member> [Grund] um einen Spieler zu töten",
        usage="<Member> [Grund]"
        )
    async def kill(self, ctx, Member: Member, *args):
        Grund = " ".join(args)
        if Grund.rstrip() == "":
            Grund = "Leer"
        VoiceState = Member.voice
        if VoiceState:
            if VoiceState.channel.permissions_for(ctx.author).move_members:
                if VoiceState.channel.permissions_for(ctx.guild.get_member(self.bot.user.id)).move_members:
                    await Member.edit(voice_channel=None,reason=Grund)
                    EMBED = Embed(title="Benutzer Getötet", color=self.color)
                    EMBED.set_footer(text=f'Auftraggeber: {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
                    EMBED.add_field(name="Betroffener",value=Member.mention)
                    EMBED.add_field(name="Grund",value=Grund)
                    await ctx.send(embed=EMBED)
                else:
                    raise commands.BotMissingPermissions([])
            else:
                raise commands.MissingPermissions([])
        else:
            EMBED = Embed(title="Töten fehlgeschlagen", color=0xff0000)
            EMBED.set_footer(text=f'Auftraggeber: {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Betroffener",value=Member.mention)
            EMBED.add_field(name="Grund",value=Grund)
            EMBED.add_field(name="Beschreibung",value="Benutzer befindet sich nicht in einem Sprachkanal!")
            await ctx.send(embed=EMBED)
        return


def setup(bot):
    bot.add_cog(Moderation(bot))
