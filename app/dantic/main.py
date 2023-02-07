import json
import typing

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

_T = typing.TypeVar("_T")
_DATA = dict | list | BaseModel | list[BaseModel] | _T | list[_T] | None


class EmbedFieldDANT(BaseModel):
    name: str
    value: str
    inline: bool = False


class EmbedDANT(BaseModel):
    title: str
    description: str
    pre_build_color: str = "default"
    fields: list[EmbedFieldDANT]


class APIResponse(BaseModel):
    """
        Base API response model

        :param ok: bool - if the request was successful
        :param data: _DATA - data to be returned
        :param error: str - error message if the request was not successful


        :return APIResponse: APIResponse - API response model
    """

    ok: bool = True

    error: str | dict = Field(None)

    data: _DATA = None

    def __call__(self, *args, **kwargs):
        return APIResponse(**kwargs)

    @classmethod
    def as_success(cls, data: _DATA = None, code: int = 200):
        return JSONResponse(
            status_code=code,
            content=json.loads(json.dumps(cls(data=data).dict(), default=str)),
            headers={"Content-Type": "application/json", "X-Error": "false"},
        )

    @classmethod
    def as_error(cls, error: str | dict, data: _DATA = None, code: int = 400):
        return JSONResponse(
            status_code=code,
            content=cls(ok=False, error=error, data=data).dict(),
            headers={"Content-Type": "application/json", "X-Error": "true"},
        )
