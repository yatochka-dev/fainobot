from prisma import models

from app.types import CommandInteraction


async def convert_title_to_item_by_title(
        inter: CommandInteraction,
        arg: str,
) -> models.Item | None:
    pass

