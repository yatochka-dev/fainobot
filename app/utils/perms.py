from fastapi import Depends
from starlette.responses import JSONResponse

from ..dantic.auth import DashboardGuildPayload
from ..services.GuildService import GuildService


async def check_endpoint_permission(
        payload: DashboardGuildPayload, service: GuildService = Depends(GuildService)
):
    guild_obj = service.bot.get_guild(int(payload.guild_id))
    if not guild_obj:
        return JSONResponse(content={"message": "Guild not found, bot is not in this guild"})

    member = guild_obj.get_member(int(payload.auth.account.providerAccountId))

    if not member:
        return JSONResponse(content={"message": "User not found in this guild"})

    permissions = member.guild_permissions
    if not any([permissions.administrator, guild_obj.owner == member]):
        return JSONResponse(content={"message": "User doesn't have permissions to view this guild"})

    return True
