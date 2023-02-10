from fastapi import APIRouter, Depends
from prisma.errors import DataError
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from app.dantic import APIResponse, ValidItemDataDANT
from app.dantic.auth import BasePayloadWithGuildIdAndAuth
from app.services.ItemService import ItemService
from app.utils.perms import check_endpoint_permission

router = APIRouter(
    prefix="/dashboard/shop",
)

include = {
    "rolesRequired": True,
    "rolesToAdd": True,
    "rolesToRemove": True,
}

order = {
    "index": "desc"
}

class BasePayload(BasePayloadWithGuildIdAndAuth):
    pass


class AddItemPayload(BasePayload):
    item: dict


@router.post("/items")
async def dashboard_get_shop_items(
        payload: BasePayload,
        service: ItemService = Depends(ItemService)
):
    perms = await check_endpoint_permission(
        payload=payload,
        service=service,
    )

    if not isinstance(perms, bool):
        return perms

    guild = service.bot.get_guild(int(payload.guild_id))

    data = await service.get_items(guild, include=include, order=order)
    resp = APIResponse.as_success(data=data)

    return resp


@router.post("/items/{item_id}")
async def dashboard_get_shop_item(
        payload: BasePayload,
        item_id: int,
        service: ItemService = Depends(ItemService)
):
    perms = await check_endpoint_permission(
        payload=payload,
        service=service,
    )

    if not isinstance(perms, bool):
        return perms

    data = await service.get_item(item_id, include=include)

    if not data:
        return APIResponse.as_error(code=404, error="No item been found")

    return APIResponse.as_success(data=data)

@router.delete("/items/{item_id}")
async def dashboard_get_shop_item(
        payload: BasePayload,
        item_id: int,
        service: ItemService = Depends(ItemService)
):
    perms = await check_endpoint_permission(
        payload=payload,
        service=service,
    )

    if not isinstance(perms, bool):
        return perms

    data = await service.delete_item(item_id)

    if not data:
        return APIResponse.as_error(code=404, error="No item been found")

    return APIResponse.as_success(data={
        "deleted": True
    })


@router.put("/items/add")
async def dashboard_add_shop_item(
        payload: AddItemPayload,
        service: ItemService = Depends(ItemService)
):
    service.bot.logger.debug("dashboard_add_shop_item")
    service.bot.logger.debug(f"{payload=!r}")

    perms = await check_endpoint_permission(
        payload=payload,
        service=service,
    )

    if not isinstance(perms, bool):
        return perms

    try:
        item_as_dict = payload.item

        validated_item_data = ValidItemDataDANT.from_api(item_as_dict)

    except ValidationError as e:
        return APIResponse.as_error(code=400, error=f"Validation error {e}")
    except ValueError as e:
        return APIResponse.as_error(code=400, error=f"Validation error {e}")

    try:
        guild = service.bot.get_guild(int(payload.guild_id))

        created_item = await service.create_item(
            guild=guild,
            data=validated_item_data,
            include=include
        )
    except ValueError as e:
        return APIResponse.as_error(code=400, error=f"Creating error {e}")
    except DataError as e:
        return APIResponse.as_error(code=400, error=f"Creating error {e}")
    except Exception as e:
        return APIResponse.as_error(code=500, error=f"Creating error {e}")

    return APIResponse.as_success(data=created_item, code=status.HTTP_201_CREATED)
