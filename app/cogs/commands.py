import disnake
from disnake.ext.commands import Cog, slash_command

from app import Bot, Embed
from app.services.cache.MemberCache import MemberCacheService
from app.types import CommandInteraction
from app.views import MembersView


class Command(Cog, MemberCacheService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="members"
    )
    async def members(self, inter: CommandInteraction, role: disnake.Role = None):

        members = inter.guild.members if not role else role.members

        fields = [
            Embed.create_field(
                name=f"{member.id}",
                value=f"{member.mention}",
                inline=True
            )
            for member in members
        ]

        embed = Embed(
            title="Members",
            user=inter.user,
        )

        pages = embed.paginate(
            fields=fields,
            max_size=10
        )

        view = MembersView(pages=pages, user=inter.user, bot=self.bot)

        await inter.send(embed=pages[0], view=view)






def setup(bot: Bot):
    bot.add_cog(Command(bot))
