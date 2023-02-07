import time

import disnake
from disnake.ext.commands import Cog

from app import Bot
from app.services.RoleService import RoleService


class RolesManagement(Cog, RoleService):

    def __init__(self, bot: Bot):
        self.bot = bot


    @Cog.listener(
        "on_ready"
    )
    async def on_ready(self):
        created, deleted, took = await self.sync_bot_roles()
        self.bot.logger.info(f"Created {created} roles, deleted {deleted} roles in {took} seconds")


    @Cog.listener(
        "on_guild_role_create"
    )
    async def on_guild_role_create(self, role: disnake.Role):
        start = time.perf_counter()
        await self.add_role(role)
        took = time.perf_counter() - start
        self.bot.logger.info(f"Created role {role.name} in {took} seconds")

    @Cog.listener(
        "on_guild_role_delete"
    )
    async def on_guild_role_delete(self, role: disnake.Role):
        start = time.perf_counter()
        await self.delete_role(role)
        took = time.perf_counter() - start
        self.bot.logger.info(f"Deleted role {role.name} in {took} seconds")


def setup(bot: Bot):
    bot.add_cog(RolesManagement(bot))
