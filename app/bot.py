import datetime
import random
from pathlib import Path

import disnake.mixins
import pydantic.main
from aiocache import Cache
from disnake.ext.commands import InteractionBot
from pydantic import BaseSettings

from .db import prisma

# from .exceptions import BotException
from .loggs import logger, disnake_logger

__all__ = ["Bot", "Settings"]

from .types import SupportsIntCast, DiscordUtilizer


class AppSettings(BaseSettings):
    TESTING: bool = True
    TIMEZONE = datetime.timezone(offset=datetime.timedelta(hours=3), name="UTC")

    github_link = "https://github.com/yatochka-dev/discord-bot-boilerplate"

    # EMBED SETTINGS
    RGB_DEFAULT_COLOR: disnake.Color = disnake.Color.from_rgb(255, 255, 255)
    RGB_ERROR_COLOR: disnake.Color = disnake.Color.from_rgb(255, 0, 0)
    RGB_SUCCESS_COLOR: disnake.Color = disnake.Color.from_rgb(0, 255, 0)
    RGB_WARNING_COLOR: disnake.Color = disnake.Color.from_rgb(255, 255, 0)
    RGB_INFO_COLOR: disnake.Color = disnake.Color.from_rgb(0, 255, 255)

    # if none - won't be added
    AUTHOR_DISPLAY_NAME: str | None = None
    ICON_URL: str | None = None


Settings = AppSettings()


@property
def snowflake(self):
    return str(self.id)


@property
def id_(self) -> int | None:
    if hasattr(self, "snowflake"):
        snowflake_ = self.snowflake
        if isinstance(snowflake_, SupportsIntCast):
            return int(snowflake_)

    return None


class Bot(InteractionBot):
    def __init__(self, *args, **kwargs):
        intents = disnake.Intents.default()
        intents.members = True
        intents.guild_scheduled_events = True

        self.cache = Cache()

        self.APP_SETTINGS = AppSettings()
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.logger = logger
        self.prisma = prisma
        self.disnake_logger = disnake_logger

        disnake.mixins.Hashable.snowflake = snowflake  # noqa
        pydantic.main.BaseModel.id_ = id_  # noqa

        super().__init__(*args, **kwargs, intents=intents)

    @property
    def now(self):
        return datetime.datetime.now(tz=self.APP_SETTINGS.TIMEZONE)

    def get_cancel_button(self, user: DiscordUtilizer):
        return disnake.ui.Button(
            style=disnake.ButtonStyle.gray,
            custom_id=f"deleteOriginalMessage_{user.id}",
            emoji=disnake.utils.get(self.emojis, name=f"deleteMessageEmoji{random.randint(1, 2)}")
            or "❌",
        )
