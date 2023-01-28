from fastapi import APIRouter, Depends
from prisma.enums import Language
from prisma.models import GuildSettings

from app.dantic.auth import DashboardGuildPayload
from app.services.GuildService import GuildService
from app.utils.perms import check_endpoint_permission

router = APIRouter(
    prefix="/dashboard/settings",
)


class SettingsResponse(GuildSettings):
    guildId: int | None
    language: str


class UpdateSettingsPayload(DashboardGuildPayload):
    data: SettingsResponse


@router.post("/general", response_model=SettingsResponse)
async def settings_get_general(
    payload: DashboardGuildPayload, service: GuildService = Depends(GuildService)
):
    perms = await check_endpoint_permission(payload, service)

    if not isinstance(perms, bool):
        return perms

    guild = await service.get_guild(int(payload.guild_id), include={"settings": True})

    response = {
        key: value for key, value in guild.settings.__dict__.items() if not key.startswith("_")
    }

    response.update(
        {
            "language": guild.language,
        }
    )

    return response


# Edit


@router.post("/general/update")
async def settings_update_general(
    payload: UpdateSettingsPayload, service: GuildService = Depends(GuildService)
):
    perms = await check_endpoint_permission(payload, service)

    if not isinstance(perms, bool):
        return perms

    guild = await service.get_guild(int(payload.guild_id), include={"settings": True})

    await service.update_general_settings(
        int(payload.guild_id), Language[payload.data.language], payload.data.dict(exclude={"guildId", "language"})
    )

    return await settings_get_general(payload, service)
