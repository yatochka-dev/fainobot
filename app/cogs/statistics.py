import disnake
from disnake.ext.commands import Cog
from disnake.ext.tasks import loop

from app.dantic import SlashCommandStats
from app.services.cache.StatisticsCache import StatisticsCacheService


class Stats(Cog, StatisticsCacheService):
    def __init__(self, bot):
        self.bot = bot
        self.save_cache_to_db.start()

        self.invoked_application_commands_interaction_ids: set[int] = set()

    @Cog.listener("on_application_command")
    async def collect_slash_command(self, inter: disnake.ApplicationCommandInteraction):
        self.bot.logger.info(
            f"Slash command invoked: {inter.application_command.name} ({inter.id})"
        )

        self.invoked_application_commands_interaction_ids.add(inter.id)

        try:
            await self.slash_command_invoked(SlashCommandStats.from_interaction(inter))
        except Exception as e:
            self.bot.logger.warn(f"Failed to save slash command to cache: {e}")
            self.invoked_application_commands_interaction_ids.remove(inter.id)

    @loop(
        seconds=60,
    )
    async def save_cache_to_db(self):
        data = await self.slash_data(
            interaction_ids=self.invoked_application_commands_interaction_ids)

        if not data:
            self.invoked_application_commands_interaction_ids.clear()
            return

        await self.bot.prisma.invokedslashcommand.create_many(data=data)
        await self.clear_slash_data()
        self.invoked_application_commands_interaction_ids.clear()

    @save_cache_to_db.before_loop
    async def before_save_cache_to_db(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Stats(bot))
