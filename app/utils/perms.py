from starlette.responses import JSONResponse

from ..dantic import APIResponse
from ..dantic.auth import BasePayloadWithGuildIdAndAuth
from ..services.index import AppService


async def check_endpoint_permission(payload: BasePayloadWithGuildIdAndAuth, service: AppService):
    guild_obj = service.bot.get_guild(int(payload.guild_id))
    if not guild_obj:
        return APIResponse.as_error(code=404, error="Guild not found")

    member = guild_obj.get_member(int(payload.auth.account.providerAccountId))

    if not member:
        return APIResponse.as_error(code=404, error="User not found in this guild")

    permissions = member.guild_permissions
    if not any([permissions.administrator, guild_obj.owner == member]):
        return APIResponse.as_error(
            code=403, error="User doesn't have permissions to access this guild"
        )

    return True
