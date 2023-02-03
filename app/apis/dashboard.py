import disnake
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dantic.auth import DiscordGuildsListForDashboard, DiscordGuild, DiscordOutsideGuild, \
    DashboardGuildPayload, GuildDantic, AuthModel
from app.services.GuildService import GuildService
from app.utils.perms import check_endpoint_permission

router = APIRouter(
    prefix="/dashboard",
)


class ResponseDiscordGuildWithMembersOnline(DiscordGuild):
    members_online: int


class InAndOutGuilds(BaseModel):
    inside: list[ResponseDiscordGuildWithMembersOnline]
    outside: list[DiscordOutsideGuild]


class Response(BaseModel):
    guilds: InAndOutGuilds


class DashResponse(BaseModel):
    guild: GuildDantic


@router.post("/guilds", response_model=Response)
async def dashboard_get_lists_of_servers(
        data: DiscordGuildsListForDashboard, service: GuildService = Depends(GuildService)
):
    async def get_guilds_where_bot_in_and_not_in(
            data_: DiscordGuildsListForDashboard,
    ) -> tuple[list[DiscordGuild], list[DiscordGuild]]:
        all_guilds = await service.get_all_guilds()
        all_guilds_snowflakes = [guild.snowflake for guild in all_guilds]
        guilds_in: list[DiscordGuild] = []
        guilds_not: list[DiscordGuild] = []
        for guild in data_.guilds:
            if guild.id in all_guilds_snowflakes:
                guilds_in.append(guild)
            else:
                guilds_not.append(guild)

        return guilds_in, guilds_not

    async def filter_guilds_by_permissions(
            discord_guilds: list[DiscordGuild],
            add_bot_to_guild: bool = False,
    ) -> list[DiscordGuild]:
        result = []
        for guild in discord_guilds:
            permissions = int(guild.permissions)

            is_owner = guild.owner
            admin_perm = (permissions & 0x8) == 0x8
            manage_guild_perm = (permissions & 0x20) == 0x20
            # perms = [is_owner, admin_perm]
            #
            # if not any(perms):
            #     discord_guilds.remove(guild)

            if is_owner:
                if add_bot_to_guild:
                    service.bot.logger.debug(
                        f"Adding bot to guild {guild.name} by owner permission"
                    )
                result.append(guild)

            elif admin_perm:
                if add_bot_to_guild:
                    service.bot.logger.debug(
                        f"Adding bot to guild {guild.name} by admin permission"
                    )
                result.append(guild)
            elif manage_guild_perm and add_bot_to_guild:
                if add_bot_to_guild:
                    service.bot.logger.debug(
                        f"Adding bot to guild {guild.name} by manage guild permission"
                    )
                result.append(guild)

        return result

    async def add_invite_link_to_guilds(
            input_guilds: list[DiscordGuild],
    ) -> list[DiscordOutsideGuild]:
        result = []
        for guild in input_guilds:
            invite_link = f'https://discord.com/oauth2/authorize?client_id=' \
                          f'{service.bot.user.id}&guild_id={guild.id}' \
                          f'&scope=applications.commands%20bot&permissions=8'

            data_ = DiscordOutsideGuild(
                id=guild.id,
                name=guild.name,
                icon=guild.icon,
                owner=guild.owner,
                permissions=guild.permissions,
                permissions_new=guild.permissions_new,
                features=guild.features,
                invite_link=invite_link,
            )

            result.append(data_)
        return result

    async def add_members_online_to_guilds(
            input_guilds: list[DiscordGuild],
    ) -> list[DiscordGuild]:
        result = []
        for guild in input_guilds:
            guild_id = int(guild.id)
            guild_obj = service.bot.get_guild(guild_id)
            members = guild_obj.members if guild_obj else []
            members_online = []
            for member in members:
                if member.status != disnake.Status.offline:
                    members_online.append(member)

            data_ = ResponseDiscordGuildWithMembersOnline(
                id=guild.id,
                name=guild.name,
                icon=guild.icon,
                owner=guild.owner,
                permissions=guild.permissions,
                permissions_new=guild.permissions_new,
                features=guild.features,
                members_online=len(members_online),
            )

            result.append(data_)
        return result

    guilds_that_bot_in, guilds_that_bot_not_in = await get_guilds_where_bot_in_and_not_in(data)
    guilds_that_bot_in = await filter_guilds_by_permissions(guilds_that_bot_in)
    guilds_that_bot_not_in = await filter_guilds_by_permissions(
        guilds_that_bot_not_in, add_bot_to_guild=True
    )

    guilds_that_bot_in = await add_members_online_to_guilds(guilds_that_bot_in)

    guilds_that_bot_not_in = await add_invite_link_to_guilds(guilds_that_bot_not_in)

    return Response(
        guilds=InAndOutGuilds(inside=guilds_that_bot_in, outside=guilds_that_bot_not_in)
    )


@router.post("/")
async def dashboard_get_guild(
        payload: DashboardGuildPayload, service: GuildService = Depends(GuildService)
):
    # This endpoint should take the payload, validate the guild and user's permissions
    # and then if user has all the permissions - return the guild data, using disnake.
    # If user doesn't have permissions - return 403 with a message.

    perms = await check_endpoint_permission(
        payload=payload,
        service=service,
    )

    if not isinstance(perms, bool):
        return perms

    guild_obj = service.bot.get_guild(int(payload.guild_id))

    guild_dantic = GuildDantic.from_snake(guild_obj)

    return DashResponse(
        guild=guild_dantic,

    )

