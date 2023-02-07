import datetime

from prisma.models import Role
from pydantic import BaseModel, validator, Field

from app import Settings
from app.utils.datendtime import parse_datetime

_ROLE = str | Role


class ValidItemDataDANT(BaseModel):
    title: str = Field(min_length=Settings.TITLE_LENGTH.min, max_length=Settings.TITLE_LENGTH.max)
    description: str | None = Field(
        min_length=Settings.DESCRIPTION_LENGTH.min, max_length=Settings.DESCRIPTION_LENGTH.max
    )
    reply: str | None = Field(
        min_length=Settings.REPLY_LENGTH.min, max_length=Settings.REPLY_LENGTH.max
    )

    stock: int | None = Field(ge=Settings.STOCK_NUMBER.min, le=Settings.STOCK_NUMBER.max)
    price: int = Field(ge=Settings.PRICE_NUMBER.min, le=Settings.PRICE_NUMBER.max)

    available_time: datetime.datetime | None

    # roles
    rolesRequired: list[_ROLE] = Field([])
    rolesToAdd: list[_ROLE] = Field([])
    rolesToRemove: list[_ROLE] = Field([])

    @validator("available_time")
    def validate_available_time(cls, available_time: datetime.datetime = None):
        if available_time is None:
            return None

        if isinstance(available_time, str):
            return parse_datetime(available_time)

        if available_time < datetime.datetime.now(tz=Settings.TIMEZONE):
            raise ValueError("available_time must be in the future")

        if available_time > datetime.datetime.now(tz=Settings.TIMEZONE) + datetime.timedelta(
                days=365
        ):
            raise ValueError("available_time must be within a year")

        return available_time

    @classmethod
    def from_api(cls, data: dict):
        roles_required: list[_ROLE] = data.get("rolesRequired", []) or []
        roles_to_add: list[_ROLE] = data.get("rolesToAdd", []) or []
        roles_to_remove: list[_ROLE] = data.get("rolesToRemove", []) or []

        # Validate roles:
        # Make sure each role is unique in each list
        # Need to check for duplicates, considering a role as a string id and as a models.Role
        # object

        def validate_list_of_roles(roles: list[_ROLE], name: str):
            roles: list[str] = [
                role.snowflake if isinstance(role, Role) else role for role in roles
            ]

            if len(roles) != len(set(roles)):
                raise ValueError(f"Duplicate roles in {name}")

            return roles

        roles_required = validate_list_of_roles(roles_required, "rolesRequired")
        roles_to_add = validate_list_of_roles(roles_to_add, "rolesToAdd")
        roles_to_remove = validate_list_of_roles(roles_to_remove, "rolesToRemove")


        return cls(
            title=data["title"],
            description=data.get("description", None),
            reply=data.get("reply", None),
            stock=data.get("stock", None),
            price=data["price"],
            available_time=data.get("available_time", None),
            rolesRequired=roles_required,
            rolesToAdd=roles_to_add,
            rolesToRemove=roles_to_remove,
        )
