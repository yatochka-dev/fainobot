from typing import Mapping

import disnake
from prisma import models
from prisma.enums import Language
from prisma.types import GuildWhereInput

from .index import CRUDXService


class GuildService(CRUDXService):
    async def add_guild(self, guild: disnake.Guild) -> models.Guild:
        self.bot.logger.debug(f"Adding guild: {guild.name} (ID: " f"{guild.id})")
        return await self.bot.prisma.guild.create(
            data={"snowflake": guild.snowflake, "settings": {"create": {}}},
        )

    async def get_guild(self, guild_id: int, include: Mapping[str, bool] = None) -> models.Guild:
        self.bot.logger.debug(f"Getting guild by id: {guild_id}")
        guild: models.Guild = await self.bot.prisma.guild.find_first(
            where={"snowflake": self.to_safe_snowflake(guild_id)},
            include=include,
        )

        return guild

    async def get_many_guilds(
            self, where: GuildWhereInput = None, include: Mapping[str, bool] = None
    ) -> list[models.Guild]:
        return await self.bot.prisma.guild.find_many(
            where=where,
            include=include,
        )

    async def remove_guild(self, guild: disnake.Guild):
        self.bot.logger.debug(f"Removing guild: {guild.name} (ID: {guild.id})")
        return await self.bot.prisma.guild.delete(
            where={"snowflake": guild.snowflake},
            include={
                "members": True,
            },
        )

    async def exists_guild(self, guild_id: int) -> bool:
        self.bot.logger.debug(f"Checking if guild exists: {guild_id}")
        return (
                await self.bot.prisma.guild.find_first(
                    where={"snowflake": self.to_safe_snowflake(guild_id)}
                )
                is not None
        )

    async def get_all_guilds(self) -> list[models.Guild]:
        self.bot.logger.debug("Getting guilds list")
        return await self.bot.prisma.guild.find_many()

    async def clean_up_database_guilds(self) -> int:
        self.bot.logger.debug("Cleaning up database")
        return await self.bot.prisma.guild.delete_many(
            where={
                "snowflake": {
                    "not": {
                        "in": [guild.snowflake for guild in self.bot.guilds],
                    },
                },
            },
        )

    # upd
    async def update_guild(self, guild: disnake.Guild, data: dict) -> models.Guild:
        self.bot.logger.debug(f"Updating guild: {guild.name} (ID: {guild.id})")
        return await self.bot.prisma.guild.update(
            where={"snowflake": guild.snowflake},
            data=data,
        )

    async def update_general_settings(
            self,
            id_: int,
            language: Language,
            settings: dict,
    ):
        self.bot.logger.debug(f"Updating general settings: (ID: {id_})")
        guild_ = self.bot.get_guild(id_)
        guild_db = await self.update_guild(
            guild_,
            {"language": language}
        )

        settings.update({"guild": {"connect": {"snowflake": guild_db.snowflake}}})

        await self.bot.prisma.guildsettings.update(
            where={
                "guildId": guild_.snowflake,
            },
            data=settings,
        )
