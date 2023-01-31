from .CacheService import CacheService
from ...dantic import SlashCommandStats
from ...types import CacheNamespaces


class StatisticsCacheService(CacheService):
    async def slash_command_invoked(
            self,
            payload: SlashCommandStats,
    ):
        namespace: str = CacheNamespaces.slash_commands_statistics.value  # noqa

        return await self.set(
            key=str(payload.interaction_id),
            value=payload.dict(),
            namespace=namespace,
        )

    async def slash_data(self, interaction_ids: set[int]):
        namespace: str = CacheNamespaces.slash_commands_statistics.value  # noqa

        data = await self.get_many(
            keys=list(map(str, interaction_ids)),
            namespace=namespace,
        )
        return data

    async def clear_slash_data(self):
        namespace: str = CacheNamespaces.slash_commands_statistics.value  # noqa

        return await self.clear(namespace=namespace)
