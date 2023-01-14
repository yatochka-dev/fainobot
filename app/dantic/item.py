import datetime

from pydantic import BaseModel, validator, Field, ValidationError

from app import MMLength
from app import Settings
from app.utils.numbers import MMNumber

TITLE_LENGTH = MMLength(min=1, max=200)
DESCRIPTION_LENGTH = MMLength(min=1, max=1024)
REPLY_LENGTH = MMLength(min=1, max=1024)
STOCK_NUMBER = MMNumber(min=1, max=1000)
PRICE_NUMBER = MMNumber(min=1, max=1000000)


class ValidItemDataDANT(BaseModel):
    title: str = Field(min_length=TITLE_LENGTH.min, max_length=TITLE_LENGTH.max)
    description: str | None = Field(
        min_length=DESCRIPTION_LENGTH.min, max_length=DESCRIPTION_LENGTH.max
    )
    reply: str | None = Field(min_length=REPLY_LENGTH.min, max_length=REPLY_LENGTH.max)

    stock: int | None = Field(ge=STOCK_NUMBER.min, le=STOCK_NUMBER.max)
    price: int = Field(ge=PRICE_NUMBER.min, le=PRICE_NUMBER.max)

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
