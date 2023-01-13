from typing import Any

from ..index import AppService


class CacheService(AppService):

    async def get(
            self,
            key: str,
            *,
            default: Any = None,
            namespace: str = None,
    ):
        return await self.bot.cache.get(key, default=default, namespace=namespace)

    async def set(
            self,
            key: str,
            value: Any,
            *,
            ttl: int = None,
            namespace: str = None,
    ):
        return await self.bot.cache.set(key, value, ttl=ttl, namespace=namespace)

    async def delete(self, key: str, *, namespace: str = None):
        return await self.bot.cache.delete(key, namespace=namespace)

    async def clear(self, *, namespace: str = None):
        return await self.bot.cache.clear(namespace=namespace)

    async def get_all(self, keys: list[str], *, namespace: str = None):
        return await self.bot.cache.multi_get(keys, namespace=namespace)

