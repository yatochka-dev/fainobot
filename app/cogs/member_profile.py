import disnake
from disnake.ext.commands import Cog, slash_command, Param, message_command

from app import Bot, Embed, EmbedField
from app.decorators import db_required
from app.exceptions import BotException
from app.services.GuildService import GuildService
from app.services.MemberService import MemberService
from app.translation.main import TranslationClient
from app.types import CommandInteractionCommunity, CommandInteraction


def get_member_from_member_and_interaction(
        interaction: CommandInteraction, _member_: disnake.Member = None
):
    if _member_ is None:
        return interaction.author
    else:
        return _member_


client = TranslationClient.get_instance()
profile_init = client.get_command_init("profile")


class MemberProfileCog(Cog, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(name=profile_init.name, description=profile_init.description)
    @db_required
    async def get_member_profile(
            self,
            inter: CommandInteractionCommunity,
            member_: disnake.Member = Param(
                None,
                name=profile_init.options["user"].name,
                description=profile_init.options["user"].description,
            ),
    ):
        _ = await self.bot.i10n.get_command_translation(inter)

        member = get_member_from_member_and_interaction(inter, member_)
        # guild_db = await self.get_guild(inter.guild_id, include={"settings": True})
        member_db = inter.member_db
        # settings = GuildSettingsFromRaw(guild_db.settings)

        fields = [
            EmbedField(
                name=_["money"],
                value=f"{member_db.money} 💵",
                inline=False,
            ),
            EmbedField(
                name=_["bank_balance"],
                value=f"{member_db.bank} 💵",
                inline=False,
            ),
            EmbedField(
                name=_["joined"],
                value=f"{disnake.utils.format_dt(member.joined_at, 'F')} ("
                      f"{disnake.utils.format_dt(member.joined_at, 'R')})",
                inline=False,
            ),
        ]

        embed = Embed(
            title=_["title"].apply(name=member.display_name),
            # title=f"{member.display_name}'s Profile",
            fields=fields,
            user=member,
        ).as_color(member.color)

        await inter.send(embed=embed, components=[self.bot.get_cancel_button(inter.author)])

    @message_command(
        name=profile_init.name,
        description=profile_init.description,
    )
    async def get_member_profile_message(
            self,
            inter: CommandInteractionCommunity,
            message: disnake.Message,
    ):
        _ = await self.bot.i10n.get_command_translation(inter)

        if message.author.bot:
            raise BotException(code=405, message=_.get_error("no_bot"))

        await self.get_member_profile(inter, message.author)

    async def cog_slash_command_check(self, inter: CommandInteraction, *args, **kwargs) -> bool:
        member = inter.options.get("user", None) or inter.author
        _ = await self.bot.i10n.get_command_translation(inter)

        if member.bot:
            raise BotException(code=405, message=_.get_error("no_bot"))

        return True


def setup(bot):
    bot.add_cog(MemberProfileCog(bot))
