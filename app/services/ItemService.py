import re

import disnake
from prisma import models

from app import Embed, EmbedField
from app.dantic import ValidItemDataDANT
from app.services.index import AppService
from app.translation.core import TranslatedString
from app.types import DiscordUtilizer

MAX_ITEMS_PER_GUILD = 200


class ItemService(AppService):
    # strings

    async def has_max_items(self, guild: models.Guild) -> tuple[bool, int]:
        count = await self.bot.prisma.item.count(where={"guild": {"snowflake": guild.snowflake}})

        return count >= MAX_ITEMS_PER_GUILD, count

    async def create_item(
            self, data: ValidItemDataDANT, guild: disnake.Guild, include: dict[str, bool] = None
    ) -> models.Item:
        self.bot.logger.debug(f"Creating item with data: {data!r}")

        count = await self.bot.prisma.item.count(where={"guild": {"snowflake": guild.snowflake}})
        guild: models.Guild = await self.bot.prisma.guild.find_unique(
            where={"snowflake": self.to_safe_snowflake(guild.id)})

        if count >= MAX_ITEMS_PER_GUILD:
            raise ValueError(
                f"This guild has reached the maximum amount of items ({MAX_ITEMS_PER_GUILD})"
            )

        current_index = guild.items_index

        await self.bot.prisma.guild.update(
            where={
                "snowflake": guild.snowflake,
            },
            data={
                "items_index": {"increment": 1},
                "items": {
                    "create": [
                        {
                            "title": data.title,
                            "description": data.description,
                            "replyMessage": data.reply,
                            "price": data.price,
                            "stock": data.stock,
                            "availableUntil": data.available_time,
                            "index": current_index,
                        }
                    ]
                }
            },
        )

        # item = await self.bot.prisma.item.create(
        #     data={
        #         "guild": {
        #             "connect": {
        #                 "snowflake": self.to_safe_snowflake(guild.id),
        #             },
        #         },
        #         "title": data.title,
        #         "description": data.description,
        #         "replyMessage": data.reply,
        #         "price": data.price,
        #         "stock": data.stock,
        #         "availableUntil": data.available_time,
        #     },
        # )
        # return item

        item = await self.bot.prisma.item.find_first(
            where={
                "guild": {
                    "snowflake": guild.snowflake,
                },
                "index": current_index,
            },
            include=include
        )

        updated = await self.bot.prisma.item.update(
            where={
                "id": item.id
            },
            data={
                "rolesRequired": {
                    "connect": [
                        {
                            "snowflake": role
                        }
                        for role in data.rolesRequired
                    ]
                },
                "rolesToAdd": {
                    "connect": [
                        {
                            "snowflake": role
                        }
                        for role in data.rolesToAdd
                    ]
                },
                "rolesToRemove": {
                    "connect": [
                        {
                            "snowflake": role
                        }
                        for role in data.rolesToRemove
                    ]
                },
            }
        )

        return updated

    async def update_item(self, item_id: int, data: ValidItemDataDANT):
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
                "availableUntil": data.available_time,
            },
        )
        return updated

    async def delete_item(self, item_id: int):
        self.bot.logger.debug(f"Deleting item with id: {item_id}")
        return await self.bot.prisma.item.delete(
            where={
                "id": item_id,
            },
        )

    async def get_item(self, item_id: int, include: dict = None) -> models.Item:
        self.bot.logger.debug(f"Getting item with id: {item_id}")
        item = await self.bot.prisma.item.find_unique(
            where={
                "id": item_id,
            },
            include=include
        )
        return item

    async def get_items(self, guild: disnake.Guild, include: dict = None, order: dict = None) -> \
            list[models.Item]:
        self.bot.logger.debug(f"Getting items for guild: {guild.id}")
        items = await self.bot.prisma.item.find_many(
            where={
                "guild": {
                    "snowflake": self.to_safe_snowflake(guild.id),
                },
            },
            include=include,
            order=order

        )
        return items

    async def get_items_by_title(
            self, guild: disnake.Guild, title: str, only_available: bool = True
    ) -> tuple[list[models.Item], bool]:

        if only_available:
            where = {
                'AND': [
                    {'title': {'contains': title}},
                    {
                        'OR': [
                            {'stock': {'gt': 0}},
                            {'stock': None}
                        ]
                    },
                    {
                        'OR': [
                            {'availableUntil': {'gt': self.bot.now}},
                            {'availableUntil': None}
                        ]
                    },
                    {
                        "guild": {
                            "snowflake": self.to_safe_snowflake(guild.id)
                        }
                    }
                ]
            }
        else:
            where = {
                'AND': [
                    {'title': {'contains': title}},
                    {
                        "guild": {
                            "snowflake": self.to_safe_snowflake(guild.id)
                        }
                    }
                ]
            }

        items = await models.Item.prisma().find_many(
            where=where
        )

        return items, len(items) >= 1

    async def get_item_from_autocomplete(self, guild: disnake.Guild, title: str):
        # Autocomplete gives string
        # Structure: "#<item.index> - <item.title>
        # Example: "#1 - Item 1"
        # We need to get the index from the string using regex

        self.bot.logger.debug(f"Getting item from autocomplete: {title!r}")

        regex = re.compile(r"#(\d+) - (.+)")

        index = regex.search(title).group(1)

        self.bot.logger.debug(f"Index: {index!r}")

        if not index:
            return None

        index = int(index)

        item = await self.bot.prisma.item.find_first(
            where={
                "index": {"equals": index},
                "guild": {"snowflake": self.to_safe_snowflake(guild.id)},
            }
        )

        return item

    async def item_to_embed(
            self,
            item: models.Item,
            user: DiscordUtilizer,
            title: str | TranslatedString = "Item `#{item.index}`",
            desc: str | TranslatedString = None,
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
                    value=f"{disnake.utils.format_dt(item.availableUntil)} ("
                          f"{disnake.utils.format_dt(item.availableUntil, 'R')})",
                    inline=False,
                )
            )

        if isinstance(title, TranslatedString):
            title = title.apply(item=item)
        elif title:
            title = title.format(item=item)

        if isinstance(desc, TranslatedString):
            desc = desc.apply(item=item)
        elif desc:
            desc = desc.format(item=item)

        embed = Embed(
            title=title if title else None,
            description=desc if desc else None,
            fields=fields,
            user=user or self.bot,
        )

        return embed

    async def get_member_inventory(self, member: models.Member) -> list[models.InventoryItem]:
        self.bot.logger.debug(f"Getting inventory for member: {member.id}")

        inventory = await self.bot.prisma.inventoryitem.find_many(
            where={
                "owner": {
                    "id": member.id,
                },
            },
        )

        return inventory

    async def get_items_for_use_autocomplete(self, title: str, member: disnake.Member):

        items = await self.bot.prisma.inventoryitem.find_many(
            where={
                "title": {
                    "contains": title
                },
                "owner": {
                    "guildId": self.to_safe_snowflake(member.guild.id),
                    "userId": self.to_safe_snowflake(member.id)
                }
            }
        )

        return items, len(items) >= 1

    async def get_item_from_use_autocomplete(
            self, title: str, member: disnake.Member
    ) -> models.InventoryItem | None:
        item = await self.bot.prisma.inventoryitem.find_first(
            where={
                "title": {
                    "contains": title
                },
                "owner": {
                    "guildId": self.to_safe_snowflake(member.guild.id),
                    "userId": self.to_safe_snowflake(member.id)
                }
            }
        )

        return item

    async def use_item(self, item: models.InventoryItem):
        self.bot.logger.debug(f"Using item: {item.id}")
        deleted = await self.bot.prisma.inventoryitem.delete(
            where={
                "id": item.id
            }
        )

        if not deleted:
            raise ValueError("Not found")

        return deleted.replyMessage
