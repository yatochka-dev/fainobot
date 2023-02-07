import time

import disnake
from prisma.enums import CollectType

from .index import AppService
from .. import Settings


class RoleService(AppService):

    async def add_role(
            self,
            role: disnake.Role,
    ):
        self.bot.logger.debug(f"Creating role: {role.id}")
        return await self.bot.prisma.role.create(
            data={
                "guild": {
                    "connect": {
                        "snowflake": self.to_safe_snowflake(role.guild.id),
                    },
                },
                "snowflake": self.to_safe_snowflake(role.id)
            }
        )

    async def delete_role(
            self,
            role: disnake.Role,
    ):
        self.bot.logger.debug(f"Deleting role: {role.id}")
        return await self.bot.prisma.role.delete(
            where={
                "snowflake": self.to_safe_snowflake(role.id),
            }
        )

    async def manage_role_collect(
            self,
            role: disnake.Role,
            collectType: CollectType,
            collectFixedAmount: int = None,
            collectPercentageAmount: int = None,
    ):
        if collectFixedAmount:
            if collectFixedAmount < 0:
                raise ValueError("Fixed amount must be greater than 0")
            if collectFixedAmount > Settings.PRICE_NUMBER.max:
                raise ValueError("Fixed amount must be less than 1000000")

        if collectPercentageAmount:
            if collectPercentageAmount < 0:
                raise ValueError("Percentage must be greater than 0")
            if collectPercentageAmount > 100:
                raise ValueError("Percentage must be less than 100")

        self.bot.logger.debug(f"Updating role: {role.id} collect mode: {collectType}")

        data = {
            "collectType": collectType,
        }

        if collectFixedAmount:
            data["collectFixedAmount"] = collectFixedAmount
        if collectPercentageAmount:
            data["collectPercentageAmount"] = collectPercentageAmount

        return await self.bot.prisma.role.update(
            where={
                "snowflake": self.to_safe_snowflake(role.id),
            },
            data=data,
        )

    @staticmethod
    def _is_to_be_saved(role: disnake.Role):
        return role.is_bot_managed() is False

    async def sync_bot_roles(self):
        # I have self.bot.guilds
        # Each guild has roles
        start = time.perf_counter()
        all_bot_roles = [
            (self.to_safe_snowflake(role.id), self.to_safe_snowflake(role.guild.id))
            for guild in self.bot.guilds
            for role in guild.roles
            if self._is_to_be_saved(role)
        ]
        created = await self.bot.prisma.role.create_many(
            data=[
                {
                    "snowflake": role[0],
                    "guildId": role[1],
                }
                for role in all_bot_roles
            ],
            skip_duplicates=True,
        )
        # for role in all_bot_roles:
        #     await self.bot.prisma.role.upsert(
        #         where={
        #             "snowflake": self.to_safe_snowflake(role.id)
        #         },
        #         data={
        #             "create": {
        #                 "snowflake": self.to_safe_snowflake(role.id),
        #                 "guild": {
        #                     "connect": {
        #                         "snowflake": self.to_safe_snowflake(role.guild.id),
        #                     }
        #                 }
        #             },
        #             "update": {},
        #         }
        #     )
        #     created += 1

        deleted = await self.bot.prisma.role.delete_many(
            where={
                "snowflake": {
                    "notIn": [
                        role[0]
                        for role in all_bot_roles
                    ]
                }
            }
        )

        for_ = time.perf_counter() - start
        return created, deleted, for_
