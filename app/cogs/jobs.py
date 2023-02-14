from disnake.ext.commands import Cog
from disnake.ext.tasks import loop

from app import Bot
from app.services.ItemService import ItemService


class ItemsJob(Cog, ItemService):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.delete_items.start()

    @Cog.listener(
        "on_ready"
    )
    async def on_ready(self):
        pass

    @loop(
        seconds=20,
    )
    async def delete_items(self):
        deleted = await self.validate_items()
        if not deleted:
            return

        self.bot.logger.debug(f"Deleted {deleted} not valid items")

    @delete_items.before_loop
    async def before_delete_items(self):
        await self.bot.wait_until_ready()


def setup(bot: Bot):
    bot.add_cog(ItemsJob(bot))
