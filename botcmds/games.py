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
    async def fortnite(self, ctx, Unterbefehl:str, platform:str="", playername:str=""):
        headers = {'TRN-Api-Key': os.environ.get("TRNAPIKEY")}
        try:
            if Unterbefehl == "store" or Unterbefehl == "shop": #Fortnite Store
                r = requests.get('https://api.fortnitetracker.com/v1/store', headers=headers)
                JSON = r.json()
                await ctx.sendEmbed(
                    title="Fortnite Item Shop",
                    color=self.color,
                    authorurl="http://fortnitetracker.com/",
                    authorname="Powered by Fortnitetracker"
                )
                for i in range(len(JSON)):
                    await ctx.sendEmbed(
                        title=str(JSON[i]["name"]),
                        description=("Rarity: %s \n vBucks: %s" % (JSON[i]["rarity"],JSON[i]["vBucks"])),
                        color=self.color,
                        thumbnailurl=str(JSON[i]["imageUrl"])
                    )

            elif Unterbefehl == "challenges" or Unterbefehl == "c": #Fortnite Challenges
                r = requests.get('https://api.fortnitetracker.com/v1/challenges', headers=headers)
                JSON = r.json()["items"]
                await ctx.sendEmbed(
                    title="Fortnite Challenges",
                    color=self.color,
                    fields=[((JSON[i]["metadata"][1]["value"]+" ("+JSON[i]["metadata"][3]["value"]+")"),(JSON[i]["metadata"][5]["value"]+" Battlepassstars")) for i in range(len(JSON))],
                    thumbnailurl=str(JSON[0]["metadata"][4]["value"]),
                    authorurl="http://fortnitetracker.com/",
                    authorname="Powered by Fortnitetracker",
                    inline=False
                )

            elif Unterbefehl == "stats": #Fortnite Stats
                if not platform == "" and not playername == "":
                    r = requests.get(("https://api.fortnitetracker.com/v1/profile/%s/%s" % (platform,playername)), headers=headers)
                    JSON = r.json()
                    try:
                        await ctx.sendEmbed(
                            title="Fortnite Stats von "+JSON["epicUserHandle"]+" auf "+JSON["platformNameLong"],
                            description=("Account Id: "+JSON["accountId"]),
                            color=self.color,
                            fields=[(JSON["lifeTimeStats"][i]["key"], JSON["lifeTimeStats"][i]["value"]) for i in range(len(JSON["lifeTimeStats"]))],
                            authorurl="http://fortnitetracker.com/",
                            authorname="Powered by Fortnitetracker"
                        )
                    except KeyError as e:
                        raise commands.BadArgument(message="Spieler wurde auf der angegebenen Platform nicht gefunden! Error: "+str(e))
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
            EMBED = ctx.getEmbed(title="Minecraft UUID", color=self.color, fields=[("UUID", JSON["id"], False),("Aktueller Name", JSON["name"], False)])
            if "legacy" in JSON:
                EMBED.add_field(name="Account",value="Alter Account")
            if "demo" in JSON:
                EMBED.add_field(name="Account",value="Demo Account")
            await ctx.send(embed=EMBED)

        elif Unterbefehl == "namen" or Unterbefehl == "names" or Unterbefehl == "name": #Fortnite Challenges
            JSON = getProfiles(Parameter)
            EMBED = ctx.getEmbed(title="Minecraft Namen", color=self.color, description="Sortierung: Von neu bis alt.")
            for i in JSON[::-1]:
                if "changedToAt" in i:
                    EMBED.add_field(name="Name seit "+str(datetime.datetime.fromtimestamp(int(i["changedToAt"])/1000).strftime('%d.%m.%Y %H:%M:%S')),value=i["name"], inline=False)
                else:
                    EMBED.add_field(name="Ursprünglicher Name",value=i["name"], inline=False)
            await ctx.send(embed=EMBED)

        elif Unterbefehl == "skin": #Fortnite Stats
            JSON = getSkin(Parameter)
            EMBED = ctx.getEmbed(title="Minecraft Skin", color=self.color, fields=[("Aktueller Name", JSON["name"]), ("UUID", JSON["id"])])
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
            JSON = getProfile(Parameter)
            UUID = JSON["id"]
            EMBED = ctx.getEmbed(title="Minecraft Spieler", color=self.color, fields=[("UUID", UUID)], inline=False)
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
