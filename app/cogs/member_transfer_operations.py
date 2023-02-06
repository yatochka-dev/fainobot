import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import Cog, slash_command, Param
from prisma import models

from app import Bot, Settings, Embed, EmbedField
from app.decorators import db_required
from app.exceptions import BotException
from app.services.CommunityService import CommunityService
from app.services.GuildService import GuildService
from app.services.MemberService import MemberService
from app.translation.main import TranslationClient
from app.types import CommandInteractionCommunity


client = TranslationClient.get_instance()
transfer_init = client.get_command_init("transfer")
print(transfer_init.options.get("user").name.localizations.data)
print(transfer_init.options.get("amount").name.localizations.data)
print(transfer_init.options.get("user").description.localizations.data)
print(transfer_init.options.get("amount").description.localizations.data)

class MemberTransferOperationsCog(Cog, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(name=transfer_init.name, description=transfer_init.description)
    @db_required
    async def transfer_money(
            self,
            inter: CommandInteractionCommunity,
            member: disnake.Member = Param(
                name=transfer_init.options["user"].name,
                description=transfer_init.options["user"].description,
            ),
            amount: int = Param(
                name=transfer_init.options["amount"].name,
                description=transfer_init.options["amount"].description,
                ge=Settings.PRICE_NUMBER.min,
                le=Settings.PRICE_NUMBER.max,
            ),
    ):
        """
        Transfer money to another member
        """

        _ = await self.bot.i10n.get_command_translation(inter)

        community_service = CommunityService.set_bot(self.bot)

        await community_service.process_member(
            guild=inter.guild,
            member=member,
            user=member._user,
        )

        try:
            from_member_db: models.Member = await self.transfer_money_to_member(
                inter.author, member, amount
            )
        except ValueError as e:
            raise BotException(
                500,
                #f"You do not have enough money to transfer, your balance is {inter.member_db.money}, you are trying to transfer {amount}.",
                _.get_error("not_enough").apply(
                    balance=inter.member_db.money,
                    amount=amount,
                ),
                _.get_error("title"),
            )

        fields = [
            EmbedField(
                name=_["current_balance"],
                value=f"{inter.author.mention} ({from_member_db.money})",
            ),
        ]

        embed = Embed(
            title=_["success_title"],
            # f"Successfully transferred {amount} 💵 to {member.mention}"
            description=_["success"].apply(
                amount=amount,
                mention=member.mention,
            ),
            fields=fields,
            user=inter.author,
        ).success

        await inter.send(embed=embed, components=[self.bot.get_cancel_button(inter.user)])

    async def cog_slash_command_check(self, inter: ApplicationCommandInteraction, *args, **kwargs):
        amount = inter.options.get("amount", 0)
        member = inter.options.get("member", None)

        _ = await self.bot.i10n.get_command_translation(inter)

        if member.bot:
            raise BotException(400, _.get_error('no_bot'), _.get_error("title"))

        if member == inter.author:
            raise BotException(400, _.get_error("no_self"), _.get_error("title"))

        if amount <= 0:
            raise BotException(400, _.get_error("greater_than_zero"), _.get_error("title"))

        return True


def setup(bot: Bot):
    bot.add_cog(MemberTransferOperationsCog(bot))
