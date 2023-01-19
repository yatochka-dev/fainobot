import datetime

from pydantic import BaseModel, validator, Field

from app import Settings


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

    @validator("available_time")
    def validate_available_time(cls, available_time: datetime.datetime = None):
        if available_time is None:
            return None

        if available_time < datetime.datetime.now(tz=Settings.TIMEZONE):
            raise ValueError("available_time must be in the future")

        if available_time > datetime.datetime.now(tz=Settings.TIMEZONE) + datetime.timedelta(
            days=365
        ):
            raise ValueError("available_time must be within a year")

        return available_time
