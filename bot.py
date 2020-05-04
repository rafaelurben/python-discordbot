from discord.ext import commands
from discord import Embed, Game, Streaming, Activity, ActivityType
from cmds import serverfiles

def get_prefix(client, message):
    if message.guild:
        prefixes = ['/']
    else:
        prefixes = ["/","!","$",".","-"]
    return commands.when_mentioned_or(*prefixes)(client, message)

bot = commands.Bot(command_prefix=get_prefix,description='Das ist eine Beschreibung!',case_insensitive=True, activity=Game(name="/help"))

extensionfolder = "cmds"
extensions = ['basic','support','moderation','games','help','channels','music']



@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    bot.remove_command('help')
    for extension in extensions:
        bot.load_extension(extensionfolder+"."+extension)
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

# Owner-only

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
        bot.unload_extension(extensionfolder+"."+extension)
        bot.load_extension(extensionfolder+"."+extension)
        EMBED2.add_field(name="Status",value="Reloaded category "+extension.upper()+"!")
    else:
        for extension in extensions:
            try:
                bot.unload_extension(extensionfolder+"."+extension)
            except:
                pass
            bot.load_extension(extensionfolder+"."+extension)
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
async def status(ctx, was:str="", arg1:str="", *args):
    arg2 = " ".join(args)
    if was.lower() in ["playing","spielt","game","play"]:
        await bot.change_presence(activity=Game(name=arg1+" "+arg2))
    elif was.lower() in ["streaming","streamt","stream","live","twitch"]:
        await bot.change_presence(activity=Streaming(url=arg1, name=arg2))
    elif was.lower() in ["listening","listen","hört","hören","song"]:
        await bot.change_presence(activity=Activity(type=ActivityType.listening, name=arg1+" "+arg2))
    elif was.lower() in ["watching","watch","schaut","video"]:
        await bot.change_presence(activity=Activity(type=ActivityType.watching, name=arg1+" "+arg2))
    else:
        EMBED = Embed(title="Mögliche Aktivitäten", color=0xff0000)
        EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
        EMBED.add_field(name="Game",value="spielt EIN SPIEL", inline=False)
        EMBED.add_field(name="Stream",value="streamt TWITCH-URL LIVE AUF TWITCH", inline=False)
        EMBED.add_field(name="Song",value="hört EINEN SONG", inline=False)
        EMBED.add_field(name="Video",value="schaut EIN VIDEO", inline=False)
        await ctx.send(embed=EMBED)



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
