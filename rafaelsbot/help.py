from discord.ext import commands
from discord import Embed
import random

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x000000

    @commands.command(
        name='help',
        brief='Erhalte Hilfe zu Commands',
        description='Hilfe kommt!',
        aliases=["hilfe","commands","command","?","h"],
        help="Benutze /help <Kategorie> für genauere Hilfe.",
        usage="<Kategorie>"
    )
    async def help(self, ctx, cog='all'):
        help_embed = Embed(title='Hilfe',color=self.color)
        #help_embed.set_thumbnail(url=ctx.author.avatar_url)
        help_embed.set_footer(text=f'Angefordert von {ctx.message.author.name}',icon_url=ctx.author.avatar_url)

        cogs = [c for c in self.bot.cogs.keys()]

        if cog == 'all':
            for cog in cogs:
               cog_commands = self.bot.get_cog(cog).get_commands()
               commands_list = ''
               for comm in cog_commands:
                   commands_list += f'**{comm.name}** - *{comm.brief}*\n'

               help_embed.add_field(
                   name=cog,
                   value=commands_list+'\u200b',
                   inline=False
               )

            pass
        else:
            lower_cogs = [c.lower() for c in cogs]

            if cog.lower() in lower_cogs:
                commands_list = self.bot.get_cog(cogs[ lower_cogs.index(cog.lower()) ]).get_commands()
                help_text=''

                for command in commands_list:
                    help_text += f'```/{command.name} - {command.brief}```\n' + f'Kurzbeschreibung: `{command.description}`\n' + f'Beschreibung: `{command.help}`\n\n'

                    if len(command.aliases) > 0:
                        help_text += f'Aliases: `/{"`, `/".join(command.aliases)}`\n'
                    else:
                        help_text += '\n'

                    help_text += f'Format: `/{command.name}{" "+command.usage if command.usage is not None else ""}`\n\n'

                help_embed.description = help_text
            else:
                raise commands.BadArgument("Ungültige Kategorie.\nBenutze den `/help` Befehl um alle Kategorien zu sehen.")

        await ctx.send(embed=help_embed)
        return


def setup(bot):
    bot.add_cog(Help(bot))
