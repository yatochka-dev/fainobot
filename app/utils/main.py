import random

from prisma.enums import MoneyAmountType
from prisma.models import GuildSettings

from app.types import MoneyEarnMethods


class GuildSettingsFromRaw:

    def __init__(
            self,
            settings: GuildSettings,
    ):
        self.settings = settings

    # def get_message_money_amount(self) -> float | int:
    #
    #     if self.settings.messageMoneyAmountType == MoneyAmountType.fixed:
    #         result = self.settings.messageFixedMoneyAmount
    #     elif self.settings.messageMoneyAmountType == MoneyAmountType.random:
    #         result = random.randint(
    #             self.settings.messageMinMoneyAmount,
    #             self.settings.messageMaxMoneyAmount
    #         )
    #     else:
    #         raise ValueError("Invalid message_money_amount_type")
    #
    #     return result

    def __str__(self):
        # return all functions calls with every for_ literal
        return "<GuildSettingsFromRaw settings={}>".format(self.settings)

    def get_money_amount(self, for_: MoneyEarnMethods, /) -> float | int:
        amountType = getattr(self.settings, f"{for_.lower()}MoneyAmountType")
        minAmount = getattr(self.settings, f"{for_.lower()}MinMoneyAmount")
        maxAmount = getattr(self.settings, f"{for_.lower()}MaxMoneyAmount")
        fixedAmount = getattr(self.settings, f"{for_.lower()}FixedMoneyAmount")

        if amountType == MoneyAmountType.fixed:
            result = fixedAmount
        elif amountType == MoneyAmountType.random:
            result = random.randint(minAmount, maxAmount)
        else:
            raise ValueError("Invalid message_money_amount_type")

        return result

    def get_money_is_enabled(self, for_: MoneyEarnMethods, /) -> bool:
        enabled = getattr(self.settings, f"{for_.lower()}MoneyEnabled")
        if enabled is None:
            raise ValueError(f"Invalid money_is_enabled for {for_!r}")
        return enabled

    def get_money_cooldown(self, for_: MoneyEarnMethods, /) -> int:
        cooldown = getattr(self.settings, f"{for_.lower()}MoneyCooldown")
        if cooldown is None:
            raise ValueError(f"Invalid money_cooldown for {for_!r}")
        return cooldown
