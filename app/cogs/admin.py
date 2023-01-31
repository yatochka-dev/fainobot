from disnake.ext.commands import Cog, is_owner, slash_command

from app import Bot
from app.services.cache.CacheService import CacheService
from app.types import CommandInteraction


class Admin(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @is_owner()
    @slash_command()
    async def cache(
            self, inter: CommandInteraction, func: str,
            key: str = None, value: str = None, namespace: str = None, ttl: int = None
    ):
        service = CacheService.set_bot(self.bot)

        func = getattr(service, func)

        if not func:
            return await inter.send("Invalid function")

        kwargs = {}

        if key:
            kwargs["key"] = key

        if value:
            kwargs["value"] = value

        if namespace:
            kwargs["namespace"] = namespace

        if ttl:
            kwargs["ttl"] = ttl

        result = await func(**kwargs)

        await inter.send(f"Result: {result}")


def setup(bot: Bot):
    bot.add_cog(Admin(bot))
