from discord.ext import commands
from discord import Embed
from rafaelsbot import serverfiles

def get_prefix(client, message):
    if message.guild:
        prefixes = ['/']
    else:
        prefixes = ["/","!","$",".","-"]
    return commands.when_mentioned_or(*prefixes)(client, message)

bot = commands.Bot(command_prefix=get_prefix,description='Das ist eine Beschreibung!',case_insensitive=True)

extensions = ['basic','support','moderation','music','games','help','channels']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    bot.remove_command('help')
    for extension in extensions:
        bot.load_extension("rafaelsbot."+extension)
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
    else:
        EMBED.add_field(name="Beschreibung",value="Es ist ein unbekannter Fehler aufgetreten! Vermutlich liegt er nicht bei dir, also melde ihn am besten einen Admin.")
        print("Bei '"+ctx.message.content+"' von '"+ctx.message.author.name+"' ist ein Fehler aufgetreten: "+str(error))
    if not error == "":
        EMBED.add_field(name="Text",value=error)
    await ctx.send(embed=EMBED)
    return



#Owner-only

@bot.command()
@commands.is_owner()
async def reload(ctx):
    print("Reloading...")
    EMBED = Embed(title="Reload", color=0x00ff00)
    EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    EMBED.add_field(name="Status",value="Reloading...")
    msg = await ctx.send(embed=EMBED)
    for extension in extensions:
        try:
            bot.unload_extension("rafaelsbot."+extension)
        except:
            pass
        bot.load_extension("rafaelsbot."+extension)
    print("Reloaded!")
    EMBED2 = Embed(title="Reload", color=0x00ff00)
    EMBED2.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    EMBED2.add_field(name="Status",value="Reloaded!")
    await msg.edit(embed=EMBED2)


@bot.command()
@commands.is_owner()
async def stop(ctx):
    EMBED = Embed(title="Stop", color=0xff0000)
    EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    EMBED.add_field(name="Status",value="Gestoppt!")
    msg = await ctx.send(embed=EMBED)
    await bot.logout()




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
