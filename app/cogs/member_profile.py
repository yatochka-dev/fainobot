import disnake
from disnake.ext.commands import Cog, slash_command, Param, message_command

from app import Bot, Embed, EmbedField
from app.decorators import db_required
from app.exceptions import BotException
from app.services.GuildService import GuildService
from app.services.MemberService import MemberService
from app.types import CommandInteractionCommunity, CommandInteraction


def get_member_from_member_and_interaction(
    interaction: CommandInteraction, _member_: disnake.Member = None
):
    if _member_ is None:
        return interaction.author
    else:
        return _member_


class MemberProfileCog(Cog, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(name="profile", description="Get a member's profile")
    @db_required
    async def get_member_profile(
        self,
        inter: CommandInteractionCommunity,
        member_: disnake.Member = Param(
            None,
            name="user",
            description="Member to get profile from",
        ),
    ):
        member = get_member_from_member_and_interaction(inter, member_)
        guild_db = await self.get_guild(inter.guild_id, include={"settings": True})
        member_db = inter.member_db
        # settings = GuildSettingsFromRaw(guild_db.settings)

        fields = [
            EmbedField(
                name="Money",
                value=f"{member_db.money} 💵",
                inline=False,
            ),
            EmbedField(
                name="Bank Balance",
                value=f"{member_db.bank} 💵",
                inline=False,
            ),
            EmbedField(
                name="Joined",
                value=f"{disnake.utils.format_dt(member.joined_at, 'F')}",
                inline=False,
            ),
        ]

        embed = Embed(
            title=f"{member.display_name}'s Profile",
            fields=fields,
            user=member,
        ).as_color(member.color)

        await inter.send(embed=embed, components=[self.bot.get_cancel_button(inter.author)])

    @message_command(
        name="profile",
    )
    async def get_member_profile_message(
        self,
        inter: CommandInteractionCommunity,
        message: disnake.Message,
    ):
        if message.author.bot:
            raise BotException(code=405, message="This command can't be used for bots")

        await self.get_member_profile(inter, message.author)

    async def cog_slash_command_check(self, inter: CommandInteraction, *args, **kwargs) -> bool:
        member = inter.options.get("user", None) or inter.author

        if member.bot:
            raise BotException(code=405, message=f"This command can't be used for bots")

        return True


def setup(bot):
    bot.add_cog(MemberProfileCog(bot))
