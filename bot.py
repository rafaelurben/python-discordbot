from discord.ext import commands
from discord import Embed, Activity, ActivityType, Status, Streaming, Game
from cmds import serverfiles

#

extensionfolder = "cmds"
extensions = ['basic','support','moderation','games','help','channels','music','owneronly']
sudo_ids = [285832847409807360]
sudo_seperator = "--sudo"
all_prefixes = ["/","!","$",".","-",">","?"]

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

        self.data = serverfiles.Server.getServer(self.guild.id)

        ## manupulate ctx for --sudo arg
        if int(self.author.id) in sudo_ids:
            if sudo_seperator in self.message.content:
                try:
                    msg = self.message.content
                    newmsg = msg.split(sudo_seperator)[0]
                    newmember = msg.split(sudo_seperator)[1]
                    self.message.content = newmsg
                    userid = int(newmember.lstrip(" ").lstrip("<@").lstrip("!").lstrip("&").rstrip(">") if "<@" in newmember and ">" in newmember else newmember)
                    member = self.guild.get_member(userid)
                    self.author = member
                    self.message.author = member
                except (ValueError, ) as e:
                    print("[SUDO] - Kein gültiges Mitglied: "+newmember+" - Fehler: "+e)


    def getargs(self):
        msg = self.message.content.split(" ")
        calledbymention = bool(self.prefix in all_prefixes)
        length = len(self.args)+len(self.kwargs)-int(calledbymention)
        txt = (" ".join(msg[length::])) if len(msg) > length else ""
        return txt.split(sudo_seperator)[0]

    async def sendEmbed(self, *args, message:str="", **kwargs):
        return await self.send(message, embed=self.getEmbed(*args, **kwargs))

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
    activity=Activity(type=ActivityType.listening, name="/help"),
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
        EMBED.add_field(name="Text",value=str(error) if len(str(error)) < 1024 else str(error)[-1024:-1])
    EMBED.add_field(name="Nachricht",value=ctx.message.content, inline=False)
    await ctx.send(embed=EMBED)
    return


# Hidden commands

@bot.command(aliases=["."])
async def destroy(ctx):
    pass


# Start

def run(TOKEN):
    bot.run(TOKEN,bot=True,reconnect=True)


import sys, os

if __name__ == "__main__":
    if 'DISCORD_RAFAELSBOT' in os.environ:
        run(os.environ.get('DISCORD_RAFAELSBOT'))

    elif len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        print("No TOKEN found! Enter it manually...")
        run(input("TOKEN: "))
