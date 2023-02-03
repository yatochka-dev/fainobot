import datetime

import disnake

from app import Settings
from app.types import DiscordUtilizer


def create_embeds_from_fields(
        embed: "Embed", fields: list["EmbedField"], max_size: int = 6, emb_style: str = "default"
) -> list["Embed"] | None:
    """

    @rtype: object
    """
    assert max_size <= 25, "Max size must be less or equal to 25"

    embeds = []

    chunks = disnake.utils.as_chunks(fields, max_size)
    emb: disnake.Embed = getattr(embed, emb_style)
    emb.clear_fields()
    for chunk in chunks:
        emb_c = emb.copy()
        for field in chunk:
            emb_c.add_field(name=field.name, value=field.value, inline=field.inline)

        embeds.append(emb_c)

    return embeds if embeds else None


class EmbedField:
    def __init__(self, name, value, inline=False):
        self.name = name
        self.value = value
        self.inline = inline

    def to_dict(self):
        return {"name": self.name, "value": self.value, "inline": self.inline}

    def __str__(self):
        return f"{self.name} - {self.value}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.name!r}, {self.value!r}, " f"inline={self.inline!r})"
        )


# Custom Embed
class Embed:
    BASE_TIMEZONE = Settings.TIMEZONE
    BASE_AUTHOR_ICON_URL = Settings.ICON_URL

    def __init__(
            self,
            user: DiscordUtilizer,
            thumbnail: bool = False,
            fields: list[EmbedField] | tuple[EmbedField] = (),
            *args,
            **kwargs,
    ):
        self.user = user
        self.thumbnail = thumbnail
        self.fields = fields
        self.embed = disnake.Embed(*args, **kwargs)
        self._set_footer(user)

    def _set_footer(self, user: DiscordUtilizer) -> None:
        if user.avatar:
            self.embed.set_footer(text=user.name, icon_url=user.avatar.url)
        else:
            self.embed.set_footer(text=user.name)

    def _get_default(self) -> disnake.Embed:
        # copy of the self.embed
        c = self.embed.copy()
        c.timestamp = datetime.datetime.now(tz=self.BASE_TIMEZONE)

        if Settings.AUTHOR_DISPLAY_NAME:
            c.set_author(
                name=Settings.AUTHOR_DISPLAY_NAME,
            )

        if self.fields:
            for field in self.fields:
                c.add_field(**field.to_dict())

        return c

    def as_color(self, color: disnake.Color | tuple[int, int, int]) -> disnake.Embed:

        if isinstance(color, tuple):
            color = disnake.Color.from_rgb(*color)

        # copy of the self.embed
        c = self._get_default()
        c._colour = color
        return c

    @property
    def no_color(self):
        return self._get_default()

    @property
    def default(self):
        return self.as_color(Settings.RGB_DEFAULT_COLOR)

    @property
    def error(self):
        return self.as_color(Settings.RGB_ERROR_COLOR)

    @property
    def success(self):
        return self.as_color(Settings.RGB_SUCCESS_COLOR)

    @property
    def warning(self):
        return self.as_color(Settings.RGB_WARNING_COLOR)

    @property
    def info(self):
        return self.as_color(Settings.RGB_INFO_COLOR)

    def __str__(self):
        return str(self.embed)

    @classmethod
    def create_field(cls, name, value, inline=False):
        return EmbedField(name, value, inline)

    def paginate(
            self, fields: list[EmbedField] | tuple[EmbedField] = (), max_size: int = 6,
            emb_style: str = "default"
            ):
        embeds = create_embeds_from_fields(self, fields, max_size, emb_style)
        return embeds
