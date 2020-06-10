from discord.ext import commands
from discord import Embed
import random

class EmbedGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x34b7eb

    @commands.has_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages = True)
    @commands.command(
        name='createembed',
        brief='Erstelle einen Embed',
        description='Erstelle einen Embed im Chat!',
        aliases=["cemb","embedcreate"],
        help="Benutze /createembed für Erklärungen.",
        usage="<Titel> [Argumente]"
    )
    async def createembed(self, ctx):
        text = ctx.getargs()
        if not text:
            await ctx.sendEmbed(title="Embed-Creator", description="""
Verwendung des Chat-Embed-Generators:
```/createembed <Titel>
[Beschreibung]
[Parameter1]
[Parameter2]
[...]
```
Parameter brauchen je eine Zeile und beginnen immer mit `//`.
Optionen werden immer mit `/!/` getrennt.

Verfügbare Parameter:""", color=self.color, inline=False, fields=[
        ("Feld (bis zu 25)","//field/!/<Titel>/!/<Inhalt>"),
        ("Footer","//footer/!/<Titel>/!/[Bild-URL]"),
        ("Author","//author/!/<Name>/!/[Link]"),
        ("Thumbnail", "//thumbnail/!/<Bild-URL>")
        ])
        else:
            lines = text.split("\n")
            data = {
                "title": lines.pop(0),
                "description": "",
                "color": self.color,
                "footertext": "",
                "footerurl": "",
                "authorname": "",
                "authorurl": "",
                "fields": [],
                "thumbnailurl": "",
                "timestamp": False
            }

            for line in lines:
                if len(line) >= 4 and line.startswith("//"):
                    line = line[2::]
                    options = line.split("/!/")
                    command = options.pop(0).lower()
                    if command in ["field","f","field"] and len(options) >= 2:
                        data["fields"].append(options)
                    elif command in ["footer","foot"] and len(options) >= 1:
                        data["footertext"] = options[0]
                        data["footerurl"] = options[1] if len(options) > 1 else ""
                    elif command in ["author"] and len(options) >= 1:
                        data["authorname"] = options[0]
                        data["authorurl"] = options[1] if len(options) > 1 else ""
                    elif command in ["thumbnailurl", "thumbnail", "thumb"] and len(options) >= 1:
                        data["thumbnailurl"] = options[0]

                else:
                    data["description"] += "\n"+line

            await ctx.sendEmbed(**data)

def setup(bot):
    bot.add_cog(EmbedGenerator(bot))
