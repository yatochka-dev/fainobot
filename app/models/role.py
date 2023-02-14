from prisma.models import Role
from prisma.enums import RoleIncomePlace
from prisma.fields import Json
from pydantic import BaseModel


class IncomeSettings(BaseModel):
    enabled: bool
    place: RoleIncomePlace
    amount: int
    cooldown: int

    def change(self, **kwargs):
        self.enabled = kwargs.get("enabled", self.enabled)
        self.place = kwargs.get("place", self.place)
        self.amount = kwargs.get("amount", self.amount)
        self.cooldown = kwargs.get("cooldown", self.cooldown)

        return self

class RoleM(Role):

    @property
    def incomeSettings(self):
        return IncomeSettings(
            **self.incomeSettings_
        )


    async def edit_incomeSettings(self, **kwargs):
        dt = self.incomeSettings.change(**kwargs)
        await self.prisma().update(
            where={
                "snowflake": self.snowflake,
            },
            data={
                "incomeSettings_": Json(dt.dict())
            }
        )
