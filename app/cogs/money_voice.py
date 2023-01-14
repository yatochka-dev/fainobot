from typing import AsyncGenerator

import disnake
from disnake.ext.commands import Cog
from disnake.ext.tasks import loop
from prisma import models

from app import Bot, GuildSettingsFromRaw
from app.services.CommunityService import CommunityService
from app.services.GuildService import GuildService
from app.services.MemberService import MemberService
from app.services.cache.MemberCache import MemberCacheService
from app.types import CacheNamespaces


class MemberVoiceMoneyCog(Cog, MemberCacheService, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot
        if not self.bot.APP_SETTINGS.TESTING:
            self.voice_money_loop.start()
        else:
            self.bot.logger.warn("Not starting voice money loop in testing mode")

    async def get_guilds_with_enabled_voice(self):
        guilds = await self.get_many_guilds(
            where={"settings": {"voiceMoneyEnabled": True}},
            include={
                "settings": True,
            },
        )

        if len(guilds) == 0:
            return []

        def get_guild(guild: models.Guild):
            g = self.bot.get_guild(guild.id)

            return g, guild.settings

        return list(map(get_guild, guilds))

    async def get_voice_channels(self) -> AsyncGenerator[disnake.VoiceChannel, None]:
        guilds = await self.get_guilds_with_enabled_voice()

        if len(guilds) == 0:
            return

        for guild, settings in guilds:
            for channel in guild.voice_channels:
                yield channel if len(channel.members) > 1 else None, settings if len(
                    channel.members
                ) > 1 else None

    async def assign_voice_money(self):
        async for channel, raw_settings in self.get_voice_channels():
            if not isinstance(channel, disnake.VoiceChannel):
                continue
            settings = GuildSettingsFromRaw(raw_settings)

            for member in channel.members:
                m_voice = member.voice
                if m_voice is None:
                    continue

                if (
                        m_voice.afk
                        or m_voice.self_deaf
                        or m_voice.self_mute
                        or m_voice.deaf
                        or m_voice.mute
                ):
                    continue

                under_cd, _ = await self.member_under_cooldown(
                    member.id, namespace=CacheNamespaces.member_voice_cooldown
                )

                if under_cd:
                    continue

                community_service = CommunityService.set_bot(self.bot)

                await community_service.process_member(
                    member=member,
                    user=member._user,  # noqa,
                    guild=member.guild,
                )

                amount = settings.get_money_amount("voice")

                await self.increment_member_money(
                    member, amount
                )

                await self.add_member_cooldown(
                    for_="voice",
                    settings=settings,
                    member_id=member.id,
                    namespace=CacheNamespaces.member_voice_cooldown,
                )

    @loop(seconds=5)
    async def voice_money_loop(self):
        await self.bot.wait_until_ready()
        await self.assign_voice_money()


def setup(bot: Bot):
    bot.add_cog(MemberVoiceMoneyCog(bot))
