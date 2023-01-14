import disnake
from prisma import models

from app.dantic import ValidItemDataDANT
from app.services.index import AppService

MAX_ITEMS_PER_GUILD = 1

class ItemService(AppService):
    # strings

    async def has_max_items(self, guild: models.Guild) -> tuple[bool, int]:
        count = await self.bot.prisma.item.count(
            where={
                "guild": {
                    "snowflake": guild.snowflake
                }
            }
        )

        return count >= MAX_ITEMS_PER_GUILD, count

    async def create_item(self, data: ValidItemDataDANT, guild: disnake.Guild) -> models.Item:
        self.bot.logger.debug(f"Creating item with data: {data!r}")

        count = await self.bot.prisma.item.count(
            where={
                "guild": {
                    "snowflake": guild.snowflake
                }
            }
        )

        if count >= MAX_ITEMS_PER_GUILD:
            raise ValueError(f"This guild has reached the maximum amount of items ({MAX_ITEMS_PER_GUILD})")

        item = await self.bot.prisma.item.create(
            data={
                "guild": {
                    "connect": {
                        "snowflake": self.to_safe_snowflake(guild.id),
                    },
                },
                "title": data.title,
                "description": data.description,
                "replyMessage": data.reply,
                "price": data.price,
                "stock": data.stock,
                "availableUntil": data.available_time,
            },
        )
        return item

    async def update_item(self, item_id: str, data: ValidItemDataDANT):
        self.bot.logger.debug(f"Updating item with data: {data!r}")
        updated = await self.bot.prisma.item.update(
            where={
                "id": item_id,
            },
            data={
                "title": data.title,
                "description": data.description,
                "reply": data.reply,
                "stock": data.stock,
                "price": data.price,
                "available_time": data.available_time,
            },
        )
        return updated

    async def delete_item(self, item_id: str):
        self.bot.logger.debug(f"Deleting item with id: {item_id}")
        await self.bot.prisma.item.delete(
            where={
                "id": item_id,
            },
        )
        return None

    async def get_item(self, item_id: str) -> models.Item:
        self.bot.logger.debug(f"Getting item with id: {item_id}")
        item = await self.bot.prisma.item.find_unique(
            where={
                "id": item_id,
            },
        )
        return item

    async def get_items(self, guild: disnake.Guild) -> list[models.Item]:
        self.bot.logger.debug(f"Getting items for guild: {guild.id}")
        items = await self.bot.prisma.item.find_many(
            where={
                "guild": {
                    "snowflake": self.to_safe_snowflake(guild.id),
                },
            },
        )
        return items



