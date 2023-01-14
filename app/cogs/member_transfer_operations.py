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
from app.types import CommandInteractionCommunity


class MemberTransferOperationsCog(Cog, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(name="transfer", description="Transfer money to another member")
    @db_required
    async def transfer_money(
            self,
            inter: CommandInteractionCommunity,
            member: disnake.Member,
            amount: int = Param(
                name="amount",
                description="Amount of money to transfer",
                ge=Settings.PRICE_NUMBER.min,
                le=Settings.PRICE_NUMBER.max,
            ),
    ):
        """
        Transfer money to another member
        """

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
                f"You do not have enough money to transfer, your balance is {inter.member_db.money}, you are trying to transfer {amount}.",
                "An error occurred while transferring money",
            )

        fields = [
            EmbedField(
                name="Current balance",
                value=f"{inter.author.mention} ({from_member_db.money})",
            ),
        ]

        embed = Embed(
            title="Money transfer",
            description=f"Successfully transferred {amount} 💵 to {member.mention}",
            fields=fields,
            user=inter.author,
        ).success

        await inter.send(embed=embed, components=[self.bot.get_cancel_button(inter.user)])

    async def cog_slash_command_check(self, inter: ApplicationCommandInteraction, *args, **kwargs):
        amount = inter.options.get("amount", 0)
        member = inter.options.get("member", None)

        if member.bot:
            raise BotException(400, "You cannot transfer money to a bot", "Bot detected")

        if member == inter.author:
            raise BotException(400, "You cannot transfer money to yourself", "Self transfer")

        if amount <= 0:
            raise BotException(400, "Amount must be greater than 0", "Invalid amount")

        return True


def setup(bot: Bot):
    bot.add_cog(MemberTransferOperationsCog(bot))
