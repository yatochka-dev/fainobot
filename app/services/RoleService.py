import time

import disnake

from .index import AppService


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
