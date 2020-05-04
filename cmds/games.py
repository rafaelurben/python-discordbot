from discord.ext import commands
from discord import Embed
import requests, datetime, base64, os


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x1f871e

    @commands.command(
        brief="Erhalte Aktuelles zu Fortnite",
        description='Sieh dir den Shop, die Herausforderungen oder die Statistiken eines Spielers an',
        aliases=['fn'],
        help="Beachte bitte, das dies noch die alten Stats sind! (Platformen: pc/xbl/psn)",
        usage="store/challenges/stats <Plattform> <Spielername>"
    )
    async def fortnite(self, ctx, Unterbefehl, platform="", playername=""):
        headers = {'TRN-Api-Key': os.environ.get("TRNAPIKEY")}
        try:
            if Unterbefehl == "store" or Unterbefehl == "shop": #Fortnite Store
                r = requests.get('https://api.fortnitetracker.com/v1/store', headers=headers)
                JSON = r.json()
                EMBED = Embed(title="Fortnite Item Shop", color=self.color)
                EMBED.set_author(url="http://fortnitetracker.com/",name="*Powered by Fortnitetracker*")
                await ctx.send(embed=EMBED)
                for i in range(len(JSON)):
                    EMBED = Embed(title=str(JSON[i]["name"]), color=self.color ,description=("Rarity: %s \n vBucks: %s" % (JSON[i]["rarity"],JSON[i]["vBucks"])))
                    EMBED.set_thumbnail(url=str(JSON[i]["imageUrl"]))
                    await ctx.send(embed=EMBED)

            elif Unterbefehl == "challenges" or Unterbefehl == "c": #Fortnite Challenges
                r = requests.get('https://api.fortnitetracker.com/v1/challenges', headers=headers)
                JSON = r.json()["items"]
                EMBED = Embed(title="Fortnite Challenges", color=self.color)
                EMBED.set_thumbnail(url=str(JSON[0]["metadata"][4]["value"]))
                for i in range(len(JSON)):
                    EMBED.add_field(name=(JSON[i]["metadata"][1]["value"]+" ("+JSON[i]["metadata"][3]["value"]+")"),value=(JSON[i]["metadata"][5]["value"]+" Battlepassstars"),inline=False)
                EMBED.set_author(url="http://fortnitetracker.com/",name="*Powered by Fortnitetracker*")
                await ctx.send(embed=EMBED)

            elif Unterbefehl == "stats": #Fortnite Stats
                if not platform == "" and not playername == "":
                    r = requests.get(("https://api.fortnitetracker.com/v1/profile/%s/%s" % (platform,playername)), headers=headers)
                    JSON = r.json()
                    try:
                        EMBED = Embed(title="Fortnite Stats von "+JSON["epicUserHandle"]+" auf "+JSON["platformNameLong"], color=self.color, description=("Account Id: "+JSON["accountId"]))
                        for i in range(len(JSON["lifeTimeStats"])):
                            EMBED.add_field(name=JSON["lifeTimeStats"][i]["key"],value=JSON["lifeTimeStats"][i]["value"])
                        EMBED.set_author(url="http://fortnitetracker.com/",name="*Powered by Fortnitetracker*")
                        await ctx.send(embed=EMBED)
                    except KeyError:
                        raise commands.BadArgument(message="Spieler wurde auf der angegebenen Platform nicht gefunden!")
                else:
                    raise commands.BadArgument(message="Platform und/oder Spieler wurde nicht angegeben!")
            else:
                raise commands.BadArgument(message="Unbekannter Unterbefehl!")
        except KeyError:
            raise commands.BadArgument(message="Scheinbar ist dieser Befehl nicht richtig konfiguriert.")


    @commands.command(
        brief="Erhalte Infos zu Minecraft-Spielern",
        description='Erhalte Informationen zu Minecraft-Spielern',
        aliases=['mc'],
        help="Benutze diesen Commands um UUIDs, Namen oder Skins von Spielern zu erhalten.",
        usage="uuid <Spielername>/namen <UUID>/skin <UUID>/player <Spielername>"
    )
    async def minecraft(self, ctx, Unterbefehl:str, Parameter:str):
        def getProfile(NAME):
            r = requests.get('https://api.mojang.com/users/profiles/minecraft/'+NAME)
            if not r.status_code == 204:
                return r.json()
            else:
                raise commands.BadArgument(message="Spieler wurde nicht gefunden!")

        def getProfiles(UUID):
            r = requests.get('https://api.mojang.com/user/profiles/'+UUID+'/names')
            if not r.status_code == 204:
                return r.json()
            else:
                raise commands.BadArgument(message="UUID wurde nicht gefunden!")

        def getSkin(UUID):
            r = requests.get('https://sessionserver.mojang.com/session/minecraft/profile/'+UUID)
            if not r.status_code == 204:
                JSON = r.json()
                if not "error" in JSON:
                    return JSON
                else:
                    raise commands.BadArgument(message="Abfrage für einen Skin kann pro UUID maximal ein Mal pro Minute erfolgen!")
            else:
                raise commands.BadArgument(message="UUID wurde nicht gefunden!")

        if Unterbefehl == "uuid" or Unterbefehl == "id": #Minecraft UUID
            JSON = getProfile(Parameter)
            EMBED = Embed(title="Minecraft UUID", color=self.color)
            EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="UUID",value=JSON["id"],inline=False)
            EMBED.add_field(name="Aktueller Name",value=JSON["name"],inline=False)
            if "legacy" in JSON:
                EMBED.add_field(name="Account",value="Alter Account")
            if "demo" in JSON:
                EMBED.add_field(name="Account",value="Demo Account")
            await ctx.send(embed=EMBED)

        elif Unterbefehl == "namen" or Unterbefehl == "names" or Unterbefehl == "name": #Fortnite Challenges
            JSON = getProfiles(Parameter)
            EMBED = Embed(title="Minecraft Namen", color=self.color, description="Sortierung: Von neu bis alt.")
            EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            for i in JSON[::-1]:
                if "changedToAt" in i:
                    EMBED.add_field(name="Name seit "+str(datetime.datetime.fromtimestamp(int(i["changedToAt"])/1000).strftime('%d.%m.%Y %H:%M:%S')),value=i["name"], inline=False)
                else:
                    EMBED.add_field(name="Ursprünglicher Name",value=i["name"], inline=False)
            await ctx.send(embed=EMBED)

        elif Unterbefehl == "skin": #Fortnite Stats
            JSON = getSkin(Parameter)
            EMBED = Embed(title="Minecraft Skin", color=self.color)
            EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Aktueller Name",value=JSON["name"])
            EMBED.add_field(name="UUID",value=JSON["id"])
            for i in JSON["properties"]:
                base64_message = i["value"]
                base64_bytes = base64_message.encode('ascii')
                message_bytes = base64.b64decode(base64_bytes)
                message = message_bytes.decode('ascii')
                dictmessage = eval(message)
                if not dictmessage["textures"] == {}:
                    skinurl = dictmessage["textures"]["SKIN"]["url"]
                    EMBED.set_thumbnail(url=skinurl)
                else:
                    EMBED.add_field(name="Skin",value="Wurde nicht gefunden. (Steve/Alex)", inline=False)
            await ctx.send(embed=EMBED)


        elif Unterbefehl == "spieler" or Unterbefehl == "player":
            EMBED = Embed(title="Minecraft Spieler", color=self.color)
            EMBED.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            JSON = getProfile(Parameter)
            UUID = JSON["id"]
            EMBED.add_field(name="UUID",value=UUID)
            if "legacy" in JSON:
                EMBED.add_field(name="Account",value="Alter Account")
            if "demo" in JSON:
                EMBED.add_field(name="Account",value="Demo Account")
            JSON2 = getProfiles(UUID)
            for i in JSON2[::-1]:
                if "changedToAt" in i:
                    EMBED.add_field(name="Name seit "+str(datetime.datetime.fromtimestamp(int(i["changedToAt"])/1000).strftime('%d.%m.%Y %H:%M:%S')),value=i["name"], inline=False)
                else:
                    EMBED.add_field(name="Ursprünglicher Name",value=i["name"], inline=False)
            JSON3 = getSkin(UUID)
            for i in JSON3["properties"]:
                base64_message = i["value"]
                base64_bytes = base64_message.encode('ascii')
                message_bytes = base64.b64decode(base64_bytes)
                message = message_bytes.decode('ascii')
                dictmessage = eval(message)
                if not dictmessage["textures"] == {}:
                    skinurl = dictmessage["textures"]["SKIN"]["url"]
                    EMBED.set_thumbnail(url=skinurl)
                else:
                    EMBED.add_field(name="Skin",value="Wurde nicht gefunden. (Steve/Alex)", inline=False)
            await ctx.send(embed=EMBED)

        else:
            raise commands.BadArgument(message="Unbekannter Unterbefehl!")
        return



def setup(bot):
    bot.add_cog(Games(bot))
