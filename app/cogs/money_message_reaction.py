import disnake
from disnake.ext.commands import Cog

from app import Bot, GuildSettingsFromRaw
from app.services.CommunityService import CommunityService
from app.services.GuildService import GuildService
from app.services.MemberService import MemberService
from app.services.cache.MemberCache import MemberCacheService
from app.types import CacheNamespaces


class MemberMoneyCog(Cog, MemberCacheService, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener(name="on_message")
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        under_cd, _ = await self.member_under_cooldown(
            member_id=message.author.id,
            namespace=CacheNamespaces.member_message_cooldown,
        )

        if under_cd:
            return

        guild = await self.get_guild(message.guild.id, include={"settings": True})

        settings = GuildSettingsFromRaw(guild.settings)

        if not settings.get_money_is_enabled("message"):
            return

        community = CommunityService.set_bot(self.bot)
        await community.process_member(
            member=message.author,
            guild=message.guild,
            user=message.author._user,  # noqa
        )

        money = settings.get_money_amount("message")

        await self.increment_member_money(
            member=message.author,
            amount=money,
        )

        self.bot.logger.debug(
            f"Added {money} to {message.author} for sending a message"
        )

        await self.add_member_cooldown(
            for_="message",
            settings=settings,
            member_id=message.author.id,
            namespace=CacheNamespaces.member_message_cooldown,
        )

    @Cog.listener(name="on_reaction_add")
    async def on_reaction_add(
            self, reaction: disnake.Reaction, member: disnake.User | disnake.Member
    ):
        if not isinstance(member, disnake.Member):
            return

        if member.bot:
            return

        if reaction.message.guild is None:
            return

        under_cd, _ = await self.member_under_cooldown(
            member_id=member.id,
            namespace=CacheNamespaces.member_reaction_cooldown,
        )

        if under_cd:
            return

        guild = await self.get_guild(reaction.message.guild.id, include={"settings": True})

        settings = GuildSettingsFromRaw(guild.settings)

        if not settings.get_money_is_enabled("reaction"):
            return

        community = CommunityService.set_bot(self.bot)
        await community.process_member(
            member=member,
            guild=member.guild,
            user=member._user,  # noqa
        )

        money = settings.get_money_amount("reaction")

        await self.increment_member_money(
            member=member,
            amount=money,
        )

        self.bot.logger.debug(
            f"Added {money} to {member} ({member.id}) for reacting to a message"
        )

        await self.add_member_cooldown(
            for_="reaction",
            settings=settings,
            member_id=member.id,
            namespace=CacheNamespaces.member_reaction_cooldown,
        )


def setup(bot: Bot):
    bot.add_cog(MemberMoneyCog(bot))
