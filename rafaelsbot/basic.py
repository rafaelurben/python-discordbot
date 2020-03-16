from discord.ext import commands
from discord import Embed, User, TextChannel, utils
from datetime import datetime as d

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
        usage="<User> [Anzahl<100] [Text]"
        )
    async def spam(self,ctx,user:User,anzahl:int=10,*args):
        anzahl = int(anzahl if anzahl <=100 else 100)
        for i in range(anzahl):
            await user.send("[Spam] "+(" ".join(str(i) for i in args)))
        return

    @commands.command(
        brief="Spamt einen Kanal voll",
        description="Schickt einem Kanal ein paar Nachrichten",
        aliases=["trollchat"],
        help="Benutze /spam <Channel> und der Bot spamt den Channel voll",
        usage="<Channel> [Anzahl<100] [Text]"
        )
    async def spamchat(self,ctx,channel:TextChannel,anzahl:int=10,*args):
        anzahl = int(anzahl if anzahl <=100 else 100)
        for i in range(anzahl):
            await channel.send("[Spam] "+(" ".join(str(i) for i in args)))
        return


def setup(bot):
    bot.add_cog(Basic(bot))
