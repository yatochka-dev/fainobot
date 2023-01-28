from fastapi import APIRouter
from prisma.enums import Language, MoneyAmountType, CollectType
from app.bot import Settings

router = APIRouter(
    prefix="/config",
)


@router.get("/public")
async def config_get_public():
    return {
        "languages": [lang for lang in Language],
        "money_amount_types": [type for type in MoneyAmountType],
        "collect_types": [type for type in CollectType],
        "min_money_amount": Settings.PRICE_NUMBER.min,
        "max_money_amount": Settings.PRICE_NUMBER.max,

    }


