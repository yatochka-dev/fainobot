import disnake
from disnake.ext.commands import Cog, slash_command

from app import Bot
from app.services.cache.MemberCache import MemberCacheService
from app.types import CommandInteraction, CacheNamespaces


class Command(Cog, MemberCacheService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="under_cooldown"
    )
    async def get_cache(self, inter: CommandInteraction, k: str):
        under_cd, until = await self.member_under_cooldown(
            member_id=inter.author.id,
            namespace=CacheNamespaces(k + "_cooldown")
        )

        content = f"Under cooldown: {under_cd}\nUntil: " \
                  f"{disnake.utils.format_dt(until) if until else 'No cooldown'}"

        await inter.send(
            content
        )


def setup(bot: Bot):
    bot.add_cog(Command(bot))
