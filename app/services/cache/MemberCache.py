import datetime

from .CacheService import CacheService
from ... import GuildSettingsFromRaw
from ...types import CacheNamespaces, MoneyEarnMethods


# r


class MemberCacheService(CacheService):

    # async def message_sent(
    #         self, message: disnake.Message, settings: GuildSettingsFromRaw
    # ) -> None:
    #     namespace: str = CacheNamespaces.member_message_cooldown.value  # noqa
    #
    #     cooldown = settings.get_money_cooldown("message")
    #
    #     await self.set(
    #         key=self.to_safe_snowflake(message.author.id),
    #         value=(self.bot.now + datetime.timedelta(seconds=cooldown)).timestamp(),
    #         namespace=namespace,
    #         ttl=cooldown,
    #     )

    async def add_member_cooldown(
        self,
        member_id: int,
        namespace: CacheNamespaces,
        for_: MoneyEarnMethods,
        settings: GuildSettingsFromRaw,
    ):
        namespace: str = namespace.value  # noqa

        cooldown = settings.get_money_cooldown(for_)
        await self.set(
            key=self.to_safe_snowflake(member_id),
            value=(self.bot.now + datetime.timedelta(seconds=cooldown)).timestamp(),
            namespace=namespace,
            ttl=cooldown,
        )

    async def member_under_cooldown(
        self, member_id: int, namespace: CacheNamespaces, *, return_until: bool = False
    ) -> tuple[bool, datetime.datetime | None]:
        namespace: str = namespace.value  # noqa

        if return_until:
            value = await self.get(
                key=self.to_safe_snowflake(member_id),
                namespace=namespace,
            )

            if value is None:
                return False, None

            return True, datetime.datetime.fromtimestamp(value)
        else:
            return await self.exists(
                key=self.to_safe_snowflake(member_id),
                namespace=namespace,
            ), None
