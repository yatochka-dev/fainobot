import disnake
from prisma import models

from app import Embed, EmbedField
from app.dantic import ValidItemDataDANT
from app.services.index import AppService
from app.types import DiscordUtilizer

MAX_ITEMS_PER_GUILD = 200


class ItemService(AppService):
    # strings

    async def has_max_items(self, guild: models.Guild) -> tuple[bool, int]:
        count = await self.bot.prisma.item.count(where={"guild": {"snowflake": guild.snowflake}})

        return count >= MAX_ITEMS_PER_GUILD, count

    async def create_item(self, data: ValidItemDataDANT, guild: disnake.Guild) -> models.Item:
        self.bot.logger.debug(f"Creating item with data: {data!r}")

        count = await self.bot.prisma.item.count(where={"guild": {"snowflake": guild.snowflake}})

        if count >= MAX_ITEMS_PER_GUILD:
            raise ValueError(
                f"This guild has reached the maximum amount of items ({MAX_ITEMS_PER_GUILD})"
            )

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
        self.bot.logger.debug(f"Updating item with id {item_id} data: {data!r}")
        updated = await self.bot.prisma.item.update(
            where={
                "id": item_id,
            },
            data={
                "title": data.title,
                "description": data.description,
                "replyMessage": data.reply,
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

    async def get_items_by_title(
        self, guild: disnake.Guild, title: str
    ) -> tuple[list[models.Item], bool]:
        items = await models.Item.prisma().find_many(
            where={
                "title": {"contains": title},
                "guild": {"snowflake": self.to_safe_snowflake(guild.id)},
            }
        )

        return items, len(items) >= 1

    async def get_item_by_title(self, guild: disnake.Guild, title: str):
        item = await self.bot.prisma.item.find_first(
            where={
                "title": {"contains": title},
                "guild": {"snowflake": self.to_safe_snowflake(guild.id)},
            }
        )

        return item

    async def item_to_embed(
        self,
        item: models.Item,
        user: DiscordUtilizer,
        title: str = "Item",
        desc: str = "Id of this item is `{item.id}`, you can use it when asking for support.",
    ) -> Embed:

        fields = [
            EmbedField(name="Title", value=item.title, inline=False),
            EmbedField(name="Price", value=item.price, inline=False),
            EmbedField(name="Description", value=item.description or "#", inline=False),
            EmbedField(name="Reply", value=item.replyMessage or "#", inline=False),
            EmbedField(name="Stock", value=item.stock or "#", inline=False),
        ]
        if item.availableUntil:
            fields.append(
                EmbedField(
                    name="Available until",
                    value=f"{disnake.utils.format_dt(item.availableUntil)}",
                    inline=False,
                )
            )

        embed = Embed(
            title=title,
            description=desc.format(item=item),
            fields=fields,
            user=user or self.bot,
        )

        return embed
