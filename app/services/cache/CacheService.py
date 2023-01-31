from typing import Any

from ..index import AppService


class CacheService(AppService):

    async def get(
            self,
            key: Any,
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

    async def exists(self, key: str, *, namespace: str = None):
        return await self.bot.cache.exists(key, namespace=namespace)

    async def get_many(self, keys: list[str], *, namespace: str = None):
        return await self.bot.cache.multi_get(keys, namespace=namespace)

    async def get_all(
            self,
            namespace: str = None,
            keys: list[str] = None,
            skip_nulls: bool = False,
    ):
        data = self.bot.cache.multi_get(namespace=namespace, keys=keys)
        if not data:
            return []



        return [
            clean for clean in await self.bot.cache.multi_get(namespace=namespace, keys=keys) if clean or not skip_nulls
        ]

