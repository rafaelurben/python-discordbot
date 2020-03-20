from discord.ext import commands
from discord import Embed, User, Member, utils, PermissionOverwrite, Role
import typing


async def getCategory(guild):
    category = utils.get(guild.categories, name="Benutzerkanäle")
    if not category:
        categoryoverwrites = { guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False, speak=False, move_members=False, use_voice_activation=True) }
        textchanneloverwrites = { guild.default_role: PermissionOverwrite(read_messages=True, send_messages=True) }
        voicechanneloverwrites = { guild.default_role: PermissionOverwrite(read_messages=True, connect=True, speak=False, move_members=False) }
        category = await guild.create_category_channel(name="Benutzerkanäle", overwrites=categoryoverwrites, reason="Bereite Benutzerkanäle vor...")
        await category.create_text_channel(name="benutzerkanäle", overwrites=textchanneloverwrites, reason="Bereite Benutzerkanäle vor...", topic="Befehle: /textchannelcreate - /textchanneldelete")
        await category.create_voice_channel(name="Sprachkanal erstellen", overwrites=voicechanneloverwrites, reason="Bereite Benutzerkanäle vor...")
    return category


class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xee00ff

        @bot.event
        async def on_voice_state_update(member, before, after):
            category = await getCategory(member.guild)
            if before.channel and before.channel.category and before.channel.category.name.upper() == "BENUTZERKANÄLE" and "#" in before.channel.name and before.channel.members == []:
                await before.channel.delete(reason="Kanal war leer")
                channelowner = utils.get(before.channel.guild.members, name=before.channel.name.split("#")[0], discriminator=before.channel.name.split("#")[1])
                EMBED = Embed(title="Sprachkanal gelöscht!", color=self.color)
                EMBED.set_footer(text=f'Kanal von {member.name}',icon_url=member.avatar_url)
                EMBED.add_field(name="Server",value=member.guild.name)
                await channelowner.send(embed=EMBED)
            if after.channel and after.channel.name == "Sprachkanal erstellen":
                channel = utils.get(member.guild.voice_channels, name=(member.name+"#"+member.discriminator))
                if channel:
                    await member.edit(voice_channel=channel,reason="Benutzer wollte einen Kanal erstellen, besitzte aber bereits einen")
                else:
                    overwrites = { member.guild.default_role: PermissionOverwrite(connect=False,speak=True,read_messages=False), member: PermissionOverwrite(connect=True,speak=True,read_messages=True,move_members=True,mute_members=True) }
                    newchannel = await category.create_voice_channel(name=(member.name+"#"+member.discriminator),overwrites=overwrites,reason="Benutzer hat den Sprachkanal erstellt")
                    await member.edit(voice_channel=newchannel,reason="Benutzer hat den Sprachkanal erstellt")
            return


    @commands.command(
        brief='Erstelle deinen Textkanal',
        description='Erstelle deinen eigenen Textkanal',
        aliases=[],
        help="Benutze /textchannelcreate um deinen eigenen Textkanal zu erhalten",
        usage=""
    )
    @commands.bot_has_permissions(manage_channels = True)
    @commands.guild_only()
    async def textchannelcreate(self, ctx):
        category = await getCategory(ctx.guild)
        channel = utils.get(ctx.guild.text_channels, name=(ctx.author.name+"-"+ctx.author.discriminator), category=category)
        if channel:
            raise commands.BadArgument(message="Du hast bereits einen Textkanal! <#"+str(channel.id)+">")
        else:
            overwrites = { ctx.guild.default_role: PermissionOverwrite(read_messages=False), ctx.author: PermissionOverwrite(read_messages=True,send_messages=True) }
            newchannel = await category.create_text_channel(name=(ctx.author.name+"-"+ctx.author.discriminator),overwrites=overwrites)
            EMBED = Embed(title="Textkanal erstellt!", color=self.color)
            EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Kanal",value="<#"+str(newchannel.id)+">")
            await ctx.send(embed=EMBED)
        return



    @commands.command(
        brief='Lösche deinen Textkanal',
        description='Lösche deinen eigenen Textkanal',
        aliases=[],
        help="Benutze /textchanneldelete um deinen eigenen Textkanal zu löschen",
        usage=""
    )
    @commands.bot_has_permissions(manage_channels = True)
    @commands.guild_only()
    async def textchanneldelete(self, ctx):
        category = await getCategory(ctx.guild)
        channel = utils.get(ctx.guild.text_channels, name=(ctx.author.name+"-"+ctx.author.discriminator), category=category)
        if channel:
            await channel.delete(reason="Vom Benutzer gelöscht")
            EMBED = Embed(title="Textkanal gelöscht!", color=self.color)
            EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Server",value=ctx.guild.name)
            await ctx.author.send(embed=EMBED)
        else:
            raise commands.BadArgument(message="Du hattest gar keinen Textkanal!")
        return



    # @commands.command(
    #     brief='Erstelle deinen Sprachkanal',
    #     description='Erstelle deinen eigenen Sprachkanal',
    #     aliases=[],
    #     help="Benutze /voicechannelcreate um deinen eigenen Sprachkanal zu erhalten",
    #     usage=""
    # )
    # @commands.bot_has_permissions(manage_channels = True)
    # @commands.guild_only()
    # async def voicechannelcreate(self, ctx):
    #     category = await getCategory(ctx.guild)
    #     channel = utils.get(ctx.guild.voice_channels, name=(ctx.author.name+"#"+ctx.author.discriminator), category=category)
    #     if channel:
    #         if ctx.author.voice:
    #             await ctx.author.edit(voice_channel=channel,reason="Benutzer hat den Kanal erstellt")
    #         raise commands.BadArgument(message="Du hast bereits einen Sprachkanal!")
    #     else:
    #         overwrites = { ctx.guild.default_role: PermissionOverwrite(connect=False,speak=True,read_messages=False), ctx.author: PermissionOverwrite(connect=True,speak=True,read_messages=True,move_members=True,mute_members=True) }
    #         newchannel = await category.create_voice_channel(name=(ctx.author.name+"#"+ctx.author.discriminator),overwrites=overwrites,reason="Benutzer hat den Sprachkanal erstellt")
    #         EMBED = Embed(title="Sprachkanal erstellt!", color=self.color)
    #         EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    #         await ctx.send(embed=EMBED)
    #         if ctx.author.voice:
    #             await ctx.author.edit(voice_channel=newchannel,reason="Benutzer hat den Sprachkanal erstellt")
    #     return
    #
    # @commands.command(
    #     brief='Lösche deinen Sprachkanal',
    #     description='Lösche deinen eigenen Sprachkanal',
    #     aliases=[],
    #     help="Benutze /voicechanneldelete um deinen eigenen Sprachkanal zu löschen",
    #     usage=""
    # )
    # @commands.bot_has_permissions(manage_channels = True)
    # @commands.guild_only()
    # async def voicechanneldelete(self, ctx):
    #     category = await getCategory(ctx.guild)
    #     channel = utils.get(ctx.guild.voice_channels, name=(ctx.author.name+"#"+ctx.author.discriminator), category=category)
    #     if channel:
    #         await channel.delete(reason="Vom Benutzer gelöscht")
    #         EMBED = Embed(title="Sprachkanal gelöscht!", color=self.color)
    #         EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
    #         EMBED.add_field(name="Server",value=ctx.guild.name)
    #         await ctx.send(embed=EMBED)
    #     else:
    #         raise commands.BadArgument(message="Du hattest gar keinen Sprachkanal!")
    #     return


    @commands.command(
        brief='Lade jemanden in deinen Sprachkanal ein',
        description='Lade jemanden oder eine Rolle in deinen Sprachkanal ein',
        aliases=["voicechannelinvite"],
        help="Benutze /voicechanneladd <Mitglied/Rolle> um jemanden in deinen Sprachkanal eingeladen",
        usage="<Mitglied/Rolle>"
    )
    @commands.bot_has_permissions(manage_channels = True)
    @commands.guild_only()
    async def voicechanneladd(self, ctx, wer: typing.Union[Member,Role]):
        category = await getCategory(ctx.guild)
        channel = utils.get(ctx.guild.voice_channels, name=(ctx.author.name+"#"+ctx.author.discriminator), category=category)
        if not channel:
            raise commands.BadArgument(message="Du hast noch keinen Sprachkanal!")
        else:
            await channel.set_permissions(wer,reason="Benuter hat Benutzer/Rolle eingeladen",read_messages=True,connect=True,speak=True)
            EMBED = Embed(title="Benutzer zu Sprachkanal eingeladen", color=self.color)
            EMBED.set_footer(text=f'Kanal von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)
            EMBED.add_field(name="Wen?",value=wer.mention)
            await ctx.send(embed=EMBED)
        return



def setup(bot):
    bot.add_cog(Channels(bot))
