import disnake
from prisma.enums import CollectType

from .index import AppService
from .. import Settings


class RoleService(AppService):

    async def create_role(
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

    async def sync_bot_roles(self):
        # I have self.bot.guilds
        # Each guild has roles

        all_bot_roles = [
            role
            for guild in self.bot.guilds
            for role in guild.roles
            if not role.is_bot_managed()
        ]

        created = await self.bot.prisma.role.upsert(
            where={
                "snowflake": {
                    "in": [
                        self.to_safe_snowflake(role.id)
                        for role in all_bot_roles
                    ]
                },
            },
        )

        await self.bot.prisma.role.delete_many(
            where={
                "snowflake": {
                    "notIn": [
                        self.to_safe_snowflake(role.id)
                        for role in all_bot_roles
                    ]
                }
            }
        )
        return created
