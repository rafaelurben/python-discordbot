from discord.ext import commands
from discord import Embed, Game, Streaming, Activity, ActivityType, Status
from cmds import serverfiles

#

extensionfolder = "cmds"
extensions = ['basic','support','moderation','games','help','channels','music']
sudo_ids = [285832847409807360]
sudo_seperator = "--sudo"
all_prefixes = ["/","!","$",".","-",">"]

# Own functions

def get_prefix(client, message):
    if message.guild:
        prefixes = ['/']
    else:
        prefixes = all_prefixes
    return commands.when_mentioned_or(*prefixes)(client, message)

# Own classes

class MyContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ## manupulate ctx for --sudo command
        if int(self.author.id) in sudo_ids:
            if sudo_seperator in self.message.content:
                msg = self.message.content
                newmsg = msg.split(sudo_seperator)[0]
                newmember = msg.split(sudo_seperator)[1]
                self.message.content = newmsg
                userid = int(newmember.lstrip(" ").lstrip("<@").lstrip("!").lstrip("&").rstrip(">") if "<@" in newmember and ">" in newmember else newmember)
                self.author = self.guild.get_member(userid)

    def getargs(self):
        msg = self.message.content.split(" ")
        calledbymention = msg[0][0] in all_prefixes
        txt = (" ".join(msg[len(self.args)+len(self.kwargs)-int(calledbymention)::])) if len(msg) > (len(self.args)-int(calledbymention)) else ""
        return txt.split(sudo_seperator)[0]

    async def sendEmbed(self, *args, **kwargs):
        return await self.send(embed=self.getEmbed(*args, **kwargs))

    def getEmbed(self, title:str, description:str="", color:int=0x000000, fields:list=[], inline:bool=True, thumbnailurl:str=None, authorurl:str="", authorname:str=None):
        EMBED = Embed(title=title, description=description, color=color)
        EMBED.set_footer(text=f'Angefordert von {self.author.name}',icon_url=self.author.avatar_url)
        for field in fields:
            EMBED.add_field(name=field[0], value=field[1], inline=field[2] if len(field) > 2 else inline)
        if thumbnailurl is not None:
            EMBED.set_thumbnail(url=thumbnailurl)
        if authorname is not None:
            EMBED.set_author(name=authorname, url=authorurl)
        return EMBED

    async def tick(self, value):
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        try:
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            pass


class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)


# create Bot

bot = MyBot(
    command_prefix=get_prefix,
    description='Das ist eine Beschreibung!',
    case_insensitive=True,
    activity=Game(name="/help"),
    status=Status.idle
)

# Events

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    bot.remove_command('help')
    for extension in extensions:
        try:
            bot.load_extension(extensionfolder+"."+extension)
        except commands.errors.ExtensionAlreadyLoaded:
            pass
    return

@bot.event
async def on_command(ctx):
    try:
        await ctx.message.delete()
    except:
        pass

@bot.event
async def on_command_error(ctx,error):
    EMBED = Embed(title="Fehler", color=0xff0000)
    EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    if isinstance(error, commands.BadArgument):
        EMBED.add_field(name="Beschreibung",value="Du hast ungültige Argumente angegeben!")
    elif isinstance(error, commands.MissingRequiredArgument):
        EMBED.add_field(name="Beschreibung",value="Du hast ein benötigtes Argument weggelassen!")
    elif isinstance(error, commands.CommandNotFound):
        EMBED.add_field(name="Beschreibung",value="Dieser Command existiert nicht!")
        print("Command '"+ctx.message.content+"' von '"+ctx.message.author.name+"' wurde nicht gefunden")
        return # keine Nachricht senden!
    elif isinstance(error, commands.CommandError):
        EMBED.add_field(name="Beschreibung",value="Bei einem Befehl ist ein Fehler aufgetreten!")
    elif isinstance(error, commands.CommandOnCooldown):
        EMBED.add_field(name="Beschreibung",value="Warte, bis du diesen Befehl erneut benutzen kannst!")
    elif isinstance(error, commands.DisabledCommand):
        EMBED.add_field(name="Beschreibung",value="Dieser Command ist aktuell deaktiviert!")
    elif isinstance(error, commands.TooManyArguments):
        EMBED.add_field(name="Beschreibung",value="Du hast zu viele Argumente angegeben!")
    elif isinstance(error, commands.MissingPermissions):
        EMBED.add_field(name="Beschreibung",value="Du hast nicht die nötigen Berechtigungen für diesen Command!")
    elif isinstance(error, commands.BotMissingPermissions):
        EMBED.add_field(name="Beschreibung",value="Ich habe nicht die nötigen Berechtigungen für diesen Command!")
    elif isinstance(error, commands.NoPrivateMessage):
        EMBED.add_field(name="Beschreibung",value="Dieser Command kann nur auf einem Server verwendet werden!")
    elif isinstance(error, commands.PrivateMessageOnly):
        EMBED.add_field(name="Beschreibung",value="Dieser Command kann nur in Direktnachrichten werden!")
    elif isinstance(error, commands.MissingRole):
        EMBED.add_field(name="Beschreibung",value="Du hast die benötigten Rollen nicht, um diesen Befehl auszuführen!")
    elif isinstance(error, commands.MissingAnyRole):
        EMBED.add_field(name="Beschreibung",value="Du hast die benötigten Rollen nicht, um diesen Befehl auszuführen!")
    elif isinstance(error, commands.NotOwner):
        EMBED.add_field(name="Beschreibung",value="Du bist nicht Besitzer des Bots!")
        return # keine Nachricht senden!
    else:
        EMBED.add_field(name="Beschreibung",value="Es ist ein unbekannter Fehler aufgetreten! Vermutlich liegt er nicht bei dir, also melde ihn am besten einen Admin.")
        print("Bei '"+ctx.message.content+"' von '"+ctx.message.author.name+"' ist ein Fehler aufgetreten: "+str(error))
    if not error == "":
        EMBED.add_field(name="Text",value=error)
    await ctx.send(embed=EMBED)
    return


# Hidden commands

@bot.command(aliases=["."])
async def destroy(ctx):
    pass

# Owner-only Commands

@bot.command()
@commands.is_owner()
async def reload(ctx, extension:str=None):
    EMBED = Embed(title="Reload", color=0x00ff00)
    EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    EMBED.add_field(name="Status",value="Reloading...")
    msg = await ctx.send(embed=EMBED)
    EMBED2 = Embed(title="Reload", color=0x00ff00)
    EMBED2.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    if extension in extensions:
        try:
            bot.unload_extension(extensionfolder+"."+extension)
        except:
            pass
        try:
            bot.load_extension(extensionfolder+"."+extension)
        except commands.errors.ExtensionAlreadyLoaded:
            pass
        EMBED2.add_field(name="Status",value="Reloaded category "+extension.upper()+"!")
    else:
        for extension in extensions:
            try:
                bot.unload_extension(extensionfolder+"."+extension)
            except:
                pass
            try:
                bot.load_extension(extensionfolder+"."+extension)
            except commands.errors.ExtensionAlreadyLoaded:
                pass
        EMBED2.add_field(name="Status",value="Reloaded all categories!")
    await msg.edit(embed=EMBED2)


@bot.command()
@commands.is_owner()
async def stopbot(ctx):
    EMBED = Embed(title="Stop", color=0xff0000)
    EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    EMBED.add_field(name="Status",value="Gestoppt!")
    msg = await ctx.send(embed=EMBED)
    await bot.logout()


@bot.command()
@commands.is_owner()
async def activity(ctx, was:str="", arg1:str=""):
    arg2 = ctx.getargs()
    if was.lower() in ["playing","spielt","game","play"]:
        await bot.change_presence(activity=Game(name=arg1+" "+arg2))
    elif was.lower() in ["streaming","streamt","stream","live","twitch"]:
        await bot.change_presence(activity=Streaming(url=arg1, name=arg2))
    elif was.lower() in ["listening","listen","hört","hören","song"]:
        await bot.change_presence(activity=Activity(type=ActivityType.listening, name=arg1+" "+arg2))
    elif was.lower() in ["watching","watch","schaut","video"]:
        await bot.change_presence(activity=Activity(type=ActivityType.watching, name=arg1+" "+arg2))
    else:
        await ctx.sendEmbed(title="Mögliche Aktivitäten", color=0xff0000, inline=False,
            fields=[
                ("Game",    "spielt <EIN SPIEL>"),
                ("Stream",  "streamt <TWITCH-URL> <AUF TWITCH>"),
                ("Song",    "hört <SONG>"),
                ("Video",   "schaut <VIDEO>")
            ]
        )

@bot.command()
@commands.is_owner()
async def status(ctx, was:str=""):
    if was.lower() in ["on","online","green"]:
        await bot.change_presence(status=Status.online)
    elif was.lower() in ["off","offline","invisible","grey"]:
        await bot.change_presence(status=Status.invisible)
    elif was.lower() in ["dnd","donotdisturb","do_not_disturb","bittenichtstören","red"]:
        await bot.change_presence(status=Status.dnd)
    elif was.lower() in ["idle","abwesend","orange","yellow"]:
        await bot.change_presence(status=Status.idle)
    else:
        await ctx.sendEmbed(title="Mögliche Status", color=0xff0000, inline=False,
            fields=[
                ("Online (on/online)",          "-> Weisser Punkt"),
                ("Abwesend (idle)",             "-> Gelber Halbmond"),
                ("Bitte nicht stören (dnd)",    "-> Rotes Verbotsschild"),
                ("Unsichtbar (off/offline)",    "-> Grauer Ring")
            ]
        )



# Start

def run(TOKEN):
    bot.run(TOKEN,bot=True,reconnect=True)


import sys, os

if 'DISCORD_RAFAELSBOT' in os.environ:
    run(os.environ.get('DISCORD_RAFAELSBOT'))
elif len(sys.argv) > 1:
    run(sys.argv[1])
else:
    print("No TOKEN found! Enter it manually...")
    run(input("TOKEN: "))
