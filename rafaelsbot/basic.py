from discord.ext import commands
from discord import Embed, User, TextChannel, utils
from datetime import datetime as d
import typing

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xffffff

    @commands.command(
        brief="Zeigt den Ping des Bots an",
        description='Gibt den aktuellen Ping zurück',
        aliases=['p'],
        help="Gib einfach /ping ein und warte ab.",
        usage=None
    )
    async def ping(self, ctx):
        start = d.timestamp(d.now())
        EMBED = Embed(title="Aktueller Ping", color=self.color)
        EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        EMBED.add_field(name="Ping",value="Berechnen...")
        msg = await ctx.send(embed=EMBED)
        EMBED2 = Embed(title="Aktueller Ping", color=self.color)
        EMBED2.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        EMBED2.add_field(name="Ping",value=str(int(( d.timestamp( d.now() ) - start ) * 1000))+"ms")
        await msg.edit(embed=EMBED2)
        return

    @commands.command(
        brief="Schreibt dir nach",
        description="Gibt den angegebenen Text zurück",
        aliases=["copy"],
        help="Benutze /say <Text> und der Bot schickt dir den Text zurück",
        usage="<Text>"
        )
    async def say(self,ctx,Text:str,*args):
        txt = Text+" "+(" ".join(str(i) for i in args))
        await ctx.send(txt)
        return

    @commands.command(
        brief="Spamt jemanden voll",
        description="Schickt jemandem ein paar Nachrichten",
        aliases=["troll"],
        help="Benutze /spam <User> und der Bot spamt den User voll",
        usage="<Kanal/Benutzer> [Anzahl<100] [Text]"
        )
    async def spam(self,ctx,what: typing.Union[TextChannel,User],anzahl:int=10,*args):
        anzahl = int(anzahl if anzahl <=100 else 100)
        text = str(" ".join(str(i) for i in args))
        empty = not (len(text) > 0 and not text == (" "*len(text)))
        for i in range(anzahl):
            if not empty:
                await what.send(text)
            else:
                await what.send("[Spam]")
        return


    @commands.command(
        brief="Zeigt die Regeln",
        description="Schickt die Regeln in den Chat",
        aliases=["rules"],
        help="Benutze /regeln um dich oder jemand anderes daran zu erinnern!",
        usage="<Kanal/Benutzer> [Anzahl<100] [Text]"
        )
    async def regeln(self,ctx):
        EMBED = Embed(title="Regeln", color=self.color, description="Das Nichtbeachten der Regeln kann mit einem Ban, Kick oder Mute bestraft werden!")
        owner = self.bot.get_user(self.bot.owner_id)
        EMBED.set_footer(text=f'Admin dieses Bots ist {owner.name}#{owner.discriminator}',icon_url=owner.avatar_url)
        EMBED.add_field(name="1) Sei anständig",value="- Sei nett zu anderen Leuten und behandle sie so, wie auch du behandelt werden möchtest!",inline=False)
        EMBED.add_field(name="2) Spamming",     value="- Spamming ist verboten!",inline=False)
        EMBED.add_field(name="3) Werbung",      value="- Werbung ist verboten!",inline=False)
        EMBED.add_field(name="4) NSFW",         value="- Anstössige Inhalte werden sofort gelöscht und der Autor mit einem Bann bestraft! \n- Hier sind auch Kinder und Jugendliche auf diesem Server!",inline=False)
        EMBED.add_field(name="5) Sicherheit",   value="- Anweisungen von Moderatoren, Supportern und Admins müssen befolgt werden!\n- Falls jemand ohne Grund nach persönlichen Daten fragt, ignoriert bitte die Nachricht und meldet sie einem anderen Admin.\n- Sendet nie jemandem euer Passwort!",inline=False)
        EMBED.add_field(name="6) Ton",          value="- Benutzt keinen Stimmverzerrer!\n- Macht keine Unnötigen Hintergrundgeräusche!",inline=False)
        EMBED.add_field(name="7) Empfehlungen", value="- Habt Spass!",inline=False)
        msg = await ctx.send(embed=EMBED)


    @commands.command(
        brief="Erhalte eine Einladung",
        description="Schickt dir eine Einladung zum Server und Bot",
        aliases=["invitelink"],
        help="Benutze /invite und erhalte eine Einladung zu diesem Server, dem Bot-Server und einen Link, um den Bot zum eigenen Server hinzuzufügen",
        usage=""
        )
    @commands.bot_has_permissions(manage_guild = True)
    async def invite(self,ctx):
        EMBED = Embed(title="Einladung", color=self.color)
        EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        try:
            invite = await ctx.guild.vanity_invite()
        except:
            invite = utils.get(list(await ctx.guild.invites()), max_age=0, max_uses=0, temporary=False)
            if not invite:
                invite = await ctx.channel.create_invite()
        EMBED.add_field(name="Dieser Server",value=invite.url)
        EMBED.add_field(name="Bot Server",value="https://rebrand.ly/RUdiscord")
        EMBED.add_field(name="Bot",value="https://rebrand.ly/RUdiscordbot")
        await ctx.send(embed=EMBED)
        return

def setup(bot):
    bot.add_cog(Basic(bot))
