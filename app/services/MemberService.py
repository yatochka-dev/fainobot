import disnake
from prisma import models

from app.services.index import CRUDXService


class MemberService(CRUDXService):
    async def remove_member(
            self,
            member: disnake.Member,
            *,
            ignore_not_found: bool = False,
    ):
        if not isinstance(member, disnake.Member):
            raise TypeError("member must be a disnake.Member")

        exists: models.Member = await self.bot.prisma.member.find_first(
            where={
                "guild": {"snowflake": self.to_safe_snowflake(member.guild.id)},
                "user": {"snowflake": self.to_safe_snowflake(member.id)},
            },
        )

        if exists:
            await self.bot.prisma.member.delete_many(
                where={
                    "guild": {"snowflake": self.to_safe_snowflake(member.guild.id)},
                    "user": {"snowflake": self.to_safe_snowflake(member.id)},
                }
            )

        elif not ignore_not_found:
            raise ValueError("member not found")

        return None

    async def increment_member_money(
            self,
            member: disnake.Member,
            amount: int,
            *,
            raise_if_not_found: bool = False,
    ):

        if not isinstance(member, disnake.Member):
            raise TypeError("member must be a disnake.Member")

        if not isinstance(amount, int):
            raise TypeError("amount must be a int")

        exists: models.Member = await self.bot.prisma.member.find_first(
            where={
                "guild": {"snowflake": self.to_safe_snowflake(member.guild.id)},
                "user": {"snowflake": self.to_safe_snowflake(member.id)},
            },
        )

        if not exists:
            if raise_if_not_found:
                raise ValueError("member not found")
            else:
                self.bot.logger.warn(f"Member not found, member {member.name} ({member.id}).")

        updated = await self.bot.prisma.member.update(
            where={"id": exists.id}, data={"money": {"increment": amount}}
        )

        if isinstance(updated, models.Member):
            return updated
        else:
            # Probably shouldn't ever happen, but just in case

            if raise_if_not_found:
                raise ValueError("member not found")
            else:
                self.bot.logger.warn(f"Member not found, member {member.name} ({member.id}).")

        # updated = await self.bot.prisma.member.update_many(
        #     where={
        #         "guild": {"snowflake": self.to_safe_snowflake(member.guild.id)},
        #         "user": {"snowflake": self.to_safe_snowflake(member.id)},
        #     },
        #     data={
        #         "money": {"increment": amount},
        #     },
        # )
        #
        # self.bot.logger.debug(f"Updated money for {member} by {amount}.")
        #
        # if updated > 1:
        #     self.bot.logger.warn(f"Updated {updated} members money, expected 1")
        # elif updated == 0:
        #     self.bot.logger.warn(f"Updated 0 members money, expected 1, member not found")
        #
        # return None

    async def transfer_money_to_member(
            self,
            from_member: disnake.Member,
            to_member: disnake.Member,
            amount: int,
            *,
            return_to_member: bool = False,
    ):

        from_member = await self.bot.prisma.member.find_first(
            where={
                "guild": {"snowflake": self.to_safe_snowflake(from_member.guild.id)},
                "user": {"snowflake": self.to_safe_snowflake(from_member.id)},
            },
        )

        to_member = await self.bot.prisma.member.find_first(
            where={
                "guild": {"snowflake": self.to_safe_snowflake(to_member.guild.id)},
                "user": {"snowflake": self.to_safe_snowflake(to_member.id)},
            },
        )
        from_member_db_id = from_member.id
        to_member_db_id = to_member.id

        async with self.bot.prisma.batch_() as db:

            if from_member.money < amount:
                raise ValueError("from_member does not have enough money")

            db.member.update(
                where={"id": from_member_db_id}, data={"money": {"decrement": amount}}
            )

            db.member.update(
                where={"id": to_member_db_id}, data={"money": {"increment": amount}}
            )



            # db.member.update_many(
            #     where={
            #         "guild": {"snowflake": self.to_safe_snowflake(from_member.guild.id)},
            #         "user": {"snowflake": self.to_safe_snowflake(from_member.id)},
            #     },
            #     data={
            #         "money": {"decrement": amount},
            #     },
            # )
            # db.member.upsert(
            #     where={
            #         "guild": {"snowflake": self.to_safe_snowflake(to_member.guild.id)},
            #         "user": {"snowflake": self.to_safe_snowflake(to_member.id)},
            #     },
            #     data={
            #         "money": {"increment": amount},
            #     },
            # )

        if return_to_member:
            return await self.bot.prisma.member.find_unique(
                where={
                    "id": to_member_db_id,
                },
            )

        return await self.bot.prisma.member.find_unique(
            where={
                "id": from_member_db_id,
            },
        )
