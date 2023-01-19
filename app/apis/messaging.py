from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app import cb
from app.dantic import ValidItemDataDANT
from app.dantic.messaging import MessageDANT
from app.services.MessagingService import MessagingService
from app.utils.datendtime import parse_datetime

router = APIRouter()


@router.post(
    "/messages/",
)
async def send_message(message: MessageDANT, service: MessagingService = Depends(MessagingService)):
    try:
        message = await service.send_message(message.embed, message.channel_id)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error while sending message: {exc}"},
        )

    if message:
        return message.to_message_reference_dict()

    return JSONResponse(status_code=500, content={"message": "Error while sending message"})


@router.post(
    "/it/"
)
async def create_item(
        title: str,
        price: int,
        description: str = None,
        reply: str = None,
        stock: int = None,
        available_time: str = None,
):
    """

    """
    valid = ValidItemDataDANT(
        title=title,
        description=description,
        reply=reply,
        stock=stock,
        price=price,
        available_time=parse_datetime(available_time) if available_time else None,
    )

    return f"Valid: {cb(f'{valid!r}'):py}\n\n{cb(valid.json()):json}\n\n{cb(str(valid.dict())):py}"
