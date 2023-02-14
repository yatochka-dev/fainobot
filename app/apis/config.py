from fastapi import APIRouter
from prisma.enums import Language, MoneyAmountType, RoleIncomeType
from app.bot import Settings
from app.dantic import ValidItemDataDANT
router = APIRouter(
    prefix="/config",
)


@router.get("/public")
async def config_get_public():
    return {
        "languages": [lang for lang in Language],
        "money_amount_types": [type for type in MoneyAmountType],
        "collect_types": [type for type in RoleIncomeType],
        "min_money_amount": Settings.PRICE_NUMBER.min,
        "max_money_amount": Settings.PRICE_NUMBER.max,
        "creating_item": {
            "title": {
                "min": Settings.TITLE_LENGTH.min,
                "max": Settings.TITLE_LENGTH.max,
            },
            "description": {
                "min": Settings.DESCRIPTION_LENGTH.min,
                "max": Settings.DESCRIPTION_LENGTH.max,
            },
            "price": {
                "min": Settings.PRICE_NUMBER.min,
                "max": Settings.PRICE_NUMBER.max,
            },
            "stock": {
                "min": Settings.STOCK_NUMBER.min,
                "max": Settings.STOCK_NUMBER.max,
            },
            "reply": {
                "min": Settings.REPLY_LENGTH.min,
                "max": Settings.REPLY_LENGTH.max,
            },
        }
    }


