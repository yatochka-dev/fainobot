import disnake
from disnake.ext.commands import Cog
from disnake.ext.tasks import loop

from app.services.cache.StatisticsCache import StatisticsCacheService


class Stats(Cog, StatisticsCacheService):
    def __init__(self, bot):
        self.bot = bot
        self.save_cache_to_db.start()

    @Cog.listener("on_application_command")
    async def collect_slash_command(self, inter: disnake.ApplicationCommandInteraction):
        self.bot.logger.debug(
            f"Slash command invoked: {inter.application_command.qualified_name} ({inter.id})"
        )
        await self.command_invoked(inter)

    @loop(
        seconds=60,
    )
    async def save_cache_to_db(self):
        await self.save_to_db()

    @save_cache_to_db.before_loop
    async def before_save_cache_to_db(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Stats(bot))
