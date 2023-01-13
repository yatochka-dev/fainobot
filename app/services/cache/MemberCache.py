import disnake

from .CacheService import CacheService
from ...types import CacheNamespaces

# r

class MemberCacheService(CacheService):

    async def message_sent(self, message: disnake.Message) -> None:
        namespace: str = CacheNamespaces.member_message_cooldown.value  # noqa

        await self.set(
            key=self.to_safe_snowflake(message.author.id),
            value=message.created_at.timestamp(),
            namespace=namespace,
            ttl=60,
        )

    async def member_under_cooldown(self, member_id: int, namespace: CacheNamespaces):
        namespace: str = namespace.value  # noqa

        value = await self.get(
            key=self.to_safe_snowflake(member_id),
            namespace=namespace,
        )

        return value or False
