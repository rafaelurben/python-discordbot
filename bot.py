from discord.ext import commands
from discord import Embed, Activity, ActivityType, Status, Streaming, Game
from botmodules import serverfiles

#

extensionfolder = "botcmds"
extensions = ['basic','support','moderation','games','help','channels','music','owneronly','converters']
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

        if self.guild is not None:
            self.data = serverfiles.Server.getServer(self.guild.id)

            ## manupulate ctx for --sudo arg
            if int(self.author.id) in sudo_ids:
                if sudo_seperator in self.message.content:
                    try:
                        msg = self.message.content
                        newmsg = msg.split(sudo_seperator)[0]
                        newmember = msg.split(sudo_seperator)[1]
                        self.message.content = newmsg
                        userid = int(newmember.strip().lstrip("<@").lstrip("!").lstrip("&").rstrip(">") if "<@" in newmember and ">" in newmember else newmember)
                        member = self.guild.get_member(userid)
                        self.author = member
                        self.message.author = member
                    except (ValueError, ) as e:
                        print("[SUDO] - Kein gültiges Mitglied: "+newmember+" - Fehler: "+e)


    def getargs(self, raiserrorwhenmissing=False):
        msg = self.message.content.split(" ")
        calledbymention = bool(self.prefix in all_prefixes)
        length = len(self.args)+len(self.kwargs)-int(calledbymention)
        txt = (" ".join(msg[length::])) if len(msg) > length else ""
        newmessage = txt.split(sudo_seperator)[0].strip()
        if not newmessage and raiserrorwhenmissing:
            raise commands.BadArgument(message="Du hast ein wichtiges Argument vergessen!")
        return newmessage

    async def sendEmbed(self, *args, message:str="", **kwargs):
        return await self.send(message, embed=self.getEmbed(*args, **kwargs))

    def getEmbed(self, title:str, description:str="", color:int=0x000000, fields:list=[], inline:bool=True, thumbnailurl:str=None, authorurl:str="", authorname:str=None):
        EMBED = Embed(title=title, description=description, color=color)
        EMBED.set_footer(text=f'Angefordert von {self.author.name}',icon_url=self.author.avatar_url)
        for field in fields:
            EMBED.add_field(name=field[0], value=field[1], inline=field[2] if len(field) > 2 else inline)
        if thumbnailurl:
            EMBED.set_thumbnail(url=thumbnailurl.strip())
        if authorname:
            if authorurl and ("https://" in authorurl or "http://" in authorurl):
                EMBED.set_author(name=authorname, url=authorurl.strip())
            else:
                EMBED.set_author(name=authorname)
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

from botevents.on_voice_state_update import setup as on_voice_state_update_setup
on_voice_state_update_setup(bot)

from botevents.on_command_error import setup as on_command_error_setup
on_command_error_setup(bot)

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
        if self.guild is not None:
            await ctx.message.delete()
    except:
        pass


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
