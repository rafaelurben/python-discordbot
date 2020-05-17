from discord.ext import commands
from discord import Game, Streaming, Activity, ActivityType, Status
from bot import extensions, extensionfolder


class Owneronly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x000000


    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension:str=None):
        msg = await ctx.sendEmbed(title="Reload", color=self.color, fields=[("Status", "Reloading")])
        EMBED = ctx.getEmbed(title="Reload", color=self.color, fields=[])
        if extension in extensions:
            try:
                self.bot.unload_extension(extensionfolder+"."+extension)
            except:
                pass
            try:
                self.bot.load_extension(extensionfolder+"."+extension)
            except commands.errors.ExtensionAlreadyLoaded:
                pass
            EMBED.add_field(name="Status",value="Reloaded category "+extension.upper()+"!")
        else:
            for extension in extensions:
                try:
                    self.bot.unload_extension(extensionfolder+"."+extension)
                except:
                    pass
                try:
                    self.bot.load_extension(extensionfolder+"."+extension)
                except commands.errors.ExtensionAlreadyLoaded:
                    pass
            EMBED.add_field(name="Status",value="Reloaded all categories!")
        await msg.edit(embed=EMBED)


    @commands.command()
    @commands.is_owner()
    async def stopbot(self, ctx):
        await ctx.sendEmbed(title="Stop", color=self.color, fields=[("Status", "Gestoppt")])
        await self.bot.logout()


    @commands.command()
    @commands.is_owner()
    async def status(self, ctx, was:str="", was2:str="", arg1:str=""):
        arg2 = ctx.getargs()
        status = None
        activity = None
        if was.lower() in ["on","online","green"]:
            status = Status.online
        elif was.lower() in ["off","offline","invisible","grey"]:
            status = Status.invisible
        elif was.lower() in ["dnd","donotdisturb","do_not_disturb","bittenichtstören","red"]:
            status = Status.dnd
        elif was.lower() in ["idle","abwesend","orange","yellow"]:
            status = Status.idle

        if was2.lower() in ["playing","spielt","game","play"]:
            activity=Game(name=arg1+" "+arg2)
        elif was2.lower() in ["streaming","streamt","stream","live","twitch"]:
            activity=Streaming(url=arg1, name=arg2)
        elif was2.lower() in ["listening","listen","hört","hören","song"]:
            activity=Activity(type=ActivityType.listening, name=arg1+" "+arg2)
        elif was2.lower() in ["watching","watch","schaut","video"]:
            activity=Activity(type=ActivityType.watching, name=arg1+" "+arg2)

        if status is not None or activity is not None:
            await ctx.bot.change_presence(status=status, activity=activity)
        else:
            await ctx.sendEmbed(title="Mögliche Status", color=0xff0000, inline=False, description="Syntax: /status <STATUS> [AKTIVITÄT] [ARGUMENTE]",
                fields=[
                    ("Online",              "on/online"),
                    ("Abwesend",            "idle"),
                    ("Bitte nicht stören",  "dnd"),
                    ("Unsichtbar",          "off/offline")
                ]
            )
            await ctx.sendEmbed(title="Mögliche Aktivitäten", color=0xff0000, inline=False, description="Syntax: /status <STATUS> [AKTIVITÄT] [ARGUMENTE]",
                fields=[
                    ("Game",    "spielt <EIN SPIEL>"),
                    ("Stream",  "streamt <TWITCH-NAME> <LIVE AUF TWITCH>"),
                    ("Song",    "hört <SONG>"),
                    ("Video",   "schaut <VIDEO>")
                ]
            )


def setup(bot):
    bot.add_cog(Owneronly(bot))
