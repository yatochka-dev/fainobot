import dataclasses

import disnake

from app.models.role import RoleM
from .cache.CacheService import CacheService
from .index import AppService
from ..types import CacheNamespaces


@dataclasses.dataclass
class Income:
    roles: list[RoleM]


class RoleIncomeService(AppService, CacheService):

    async def is_cached(self, role: RoleM) -> bool:
        return await self.exists(
            key=role.snowflake,
            namespace=CacheNamespaces.role_income
        )

    async def save_role_to_cache(self, role: RoleM, member_id: int | str):
        ttl = role.incomeSettings.cooldown
        if ttl is None:
            ttl = 0

        key = f"{role.snowflake}:{member_id}"

        return await self.set(
            key=key,
            value=role,
            namespace=CacheNamespaces.role_income,
            ttl=ttl
        )



    @staticmethod
    async def get_roles_with_income(member: disnake.Member) -> list[RoleM]:

        member_roles = [str(role.id) for role in member.roles]

        roles = await RoleM.prisma().find_many(
            where={
                "snowflake": {
                    "in": member_roles
                },
                "incomeSettings_": {
                    "enabled": True
                }
            }
        )

        return roles

