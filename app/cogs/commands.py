import disnake
from disnake.ext.commands import Cog, slash_command

from app import Bot, md, EmbedField, GuildSettingsFromRaw
from app.decorators import db_required
from app.embedding import Embed
from app.services.cache.CacheService import CacheService
from app.services.cache.MemberCache import MemberCacheService
from app.types import CommandInteraction, CommandInteractionCommunity, CacheNamespaces
from app.utils.embeds import create_embeds_from_fields
from app.views import PaginationView


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

        content = f"Under cooldown: {under_cd}\nUntil: {disnake.utils.format_dt(until) if until else 'No cooldown'}"

        await inter.send(
            content
        )





def setup(bot: Bot):
    bot.add_cog(Command(bot))
