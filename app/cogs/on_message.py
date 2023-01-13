import disnake
from disnake import RawGuildScheduledEventUserActionEvent, GuildScheduledEvent
from disnake.ext.commands import Cog, cooldown, BucketType

from app import Bot
from app.services.cache.MemberCache import MemberCacheService
from app.types import CacheNamespaces


class MemberMessagesCog(Cog, MemberCacheService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener(
        name="on_message"
    )
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        if cooldown := await self.member_under_cooldown(
                member_id=message.author.id,
                namespace=CacheNamespaces.member_message_cooldown,
        ):
            return await message.reply(
                "You are under cooldown {}!".format(cooldown)
            )

        await self.message_sent(
            message=message
        )



def setup(bot: Bot):
    bot.add_cog(MemberMessagesCog(bot))
