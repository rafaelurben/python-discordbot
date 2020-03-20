from discord.ext import commands
from discord import Embed, User, Member, utils, PermissionOverwrite
from . import serverfiles

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xee00ff

        @bot.event
        async def on_voice_state_update(member, before, after):
            if before.channel and before.channel.category and before.channel.category.name.upper() == "BENUTZERKANÄLE" and before.channel.members == []:
                await before.channel.delete(reason="War leer")
                channelowner = utils.get(before.channel.guild.members, name=before.channel.name.split("#")[0], discriminator=before.channel.name.split("#")[1])
                EMBED = Embed(title="Sprachkanal gelöscht!", color=self.color)
                EMBED.set_footer(text=f'Kanal von {member.name}',icon_url=member.avatar_url)
                EMBED.add_field(name="Server",value=member.guild.name)
                await channelowner.send(embed=EMBED)


    @commands.bot_has_permissions(manage_channels = True)
    @commands.command(
        brief='Erstelle deinen Textkanal',
        description='Erstelle deinen eigenen Textkanal',
        aliases=[],
        help="Benutze /createtextchannel um deinen eigenen Textkanal zu erhalten",
        usage=""
    )
    async def createtextchannel(self, ctx):
        channel = utils.get(ctx.guild.text_channels, name=(ctx.author.name+"-"+ctx.author.discriminator))
        category = utils.get(ctx.guild.categories, name="Benutzerkanäle")
        if channel:
            raise commands.BadArgument(message="Du hast bereits einen Textkanal! <#"+str(channel.id)+">")
        elif category:
            overwrites = { ctx.guild.default_role: PermissionOverwrite(read_messages=False), ctx.author: PermissionOverwrite(read_messages=True,send_messages=True) }
            newchannel = await category.create_text_channel(name=(ctx.author.name+"-"+ctx.author.discriminator),overwrites=overwrites)
            EMBED = Embed(title="Textkanal erstellt!", color=self.color)
            EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Kanal",value="<#"+str(newchannel.id)+">")
            await ctx.send(embed=EMBED)
        else:
            raise commands.BadArgument(message="Es gibt noch keine Kategorie mit dem Namen Benutzerkanäle!")
        return

    @commands.bot_has_permissions(manage_channels = True)
    @commands.command(
        brief='Lösche deinen Textkanal',
        description='Lösche deinen eigenen Textkanal',
        aliases=["removetextchannel"],
        help="Benutze /deletetextchannel um deinen eigenen Textkanal zu löschen",
        usage=""
    )
    async def deletetextchannel(self, ctx):
        channel = utils.get(ctx.guild.text_channels, name=(ctx.author.name+"-"+ctx.author.discriminator))
        if channel:
            await channel.delete(reason="Vom Benutzer gelöscht")
            EMBED = Embed(title="Textkanal gelöscht!", color=self.color)
            EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Server",value=ctx.guild.name)
            await ctx.author.send(embed=EMBED)
        else:
            raise commands.BadArgument(message="Du hattest gar keinen Textkanal!")
        return



    @commands.bot_has_permissions(manage_channels = True)
    @commands.command(
        brief='Erstelle deinen Sprachkanal',
        description='Erstelle deinen eigenen Sprachkanal',
        aliases=[],
        help="Benutze /createvoicechannel um deinen eigenen Sprachkanal zu erhalten",
        usage=""
    )
    async def createvoicechannel(self, ctx):
        channel = utils.get(ctx.guild.voice_channels, name=(ctx.author.name+"#"+ctx.author.discriminator))
        category = utils.get(ctx.guild.categories, name="Benutzerkanäle")
        if channel:
            if ctx.author.voice:
                await ctx.author.edit(voice_channel=channel,reason="Benutzer hat den Kanal erstellt")
            raise commands.BadArgument(message="Du hast bereits einen Sprachkanal!")
        elif category:
            overwrites = { ctx.guild.default_role: PermissionOverwrite(connect=False,speak=True,read_messages=False), ctx.author: PermissionOverwrite(connect=True,speak=True,read_messages=True) }
            newchannel = await category.create_voice_channel(name=(ctx.author.name+"#"+ctx.author.discriminator),overwrites=overwrites)
            EMBED = Embed(title="Sprachkanal erstellt!", color=self.color)
            EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            await ctx.send(embed=EMBED)
            if ctx.author.voice:
                await ctx.author.edit(voice_channel=newchannel,reason="Benutzer hat den Sprachkanal erstellt")
        else:
            raise commands.BadArgument(message="Es gibt noch keine Kategorie mit dem Namen Benutzerkanäle!")
        return

    @commands.bot_has_permissions(manage_channels = True)
    @commands.command(
        brief='Lösche deinen Sprachkanal',
        description='Lösche deinen eigenen Sprachkanal',
        aliases=["removevoicechannel"],
        help="Benutze /deletevoicechannel um deinen eigenen Sprachkanal zu löschen",
        usage=""
    )
    async def deletevoicechannel(self, ctx):
        channel = utils.get(ctx.guild.voice_channels, name=(ctx.author.name+"#"+ctx.author.discriminator))
        if channel:
            await channel.delete(reason="Vom Benutzer gelöscht")
            EMBED = Embed(title="Sprachkanal gelöscht!", color=self.color)
            EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Server",value=ctx.guild.name)
            await ctx.send(embed=EMBED)
        else:
            raise commands.BadArgument(message="Du hattest gar keinen Sprachkanal!")
        return



def setup(bot):
    bot.add_cog(Channels(bot))
