import disnake
from pydantic import BaseModel


class Account(BaseModel):
    id: str
    userId: str
    type: str
    provider: str
    providerAccountId: str
    refresh_token: str = None
    access_token: str = None
    expires_at: int = None
    token_type: str = None
    scope: str = None
    id_token: str = None
    session_state: str = None


class DiscordUser(BaseModel):
    id: str
    username: str
    avatar: str
    user_avatar_url: str
    avatar_decoration: bool = None
    discriminator: str
    public_flags: int
    flags: int
    banner: str = None
    banner_color: str = None
    accent_color: int = None
    locale: str = None
    mfa_enabled: bool
    premium_type: int = None
    email: str = None
    verified: bool


class SessionUser(BaseModel):
    id: str
    name: str = None
    email: str = None
    image: str = None


class Session(BaseModel):
    user: SessionUser = None
    accessToken: str = None


class AuthBaseModel(BaseModel):
    account: Account
    session: Session


class AuthModel(BaseModel):
    auth: AuthBaseModel


class DiscordGuild(BaseModel):
    id: str
    name: str
    icon: str | None
    owner: bool
    permissions: int
    permissions_new: str
    features: list[str]


class DiscordOutsideGuild(BaseModel):
    id: str
    name: str
    icon: str | None
    owner: bool
    permissions: int
    permissions_new: str
    features: list[str]
    invite_link: str


class DiscordGuildsListForDashboard(AuthModel):
    guilds: list[DiscordGuild]


class Emoji(BaseModel):
    id: str | None
    name: str | None
    animated: bool

    @classmethod
    def from_snake(cls, data: disnake.Emoji, /):
        return cls(
            id=str(data.id),
            name=data.name,
            animated=data.animated,
        )

class Role(BaseModel):
    id: str
    name: str
    color: int
    hoist: bool
    position: int
    permissions: int
    managed: bool
    mentionable: bool

    @classmethod
    def from_snake(cls, data: disnake.Role, /):
        return cls(
            id=str(data.id),
            name=data.name,
            color=data.color.value,
            hoist=data.hoist,
            position=data.position,
            permissions=data.permissions.value,
            managed=data.managed,
            mentionable=data.mentionable,
        )

class GuildDantic(BaseModel):
    id: int
    name: str
    icon: str | None
    banner: str | None
    roles: list[Role] | None
    emojis: list[Emoji] | None

    # booleans
    banner_animated: bool

    @classmethod
    def from_snake(cls, data: disnake.Guild, /):
        roles = [Role.from_snake(role) for role in data.roles if not role.is_bot_managed() and not role.is_default()]
        roles.reverse()
        ret = cls(
            id=data.id,
            name=data.name,
            icon=str(data.icon.url) if data.icon else None,
            banner=str(data.banner.url) if data.banner else None,
            emojis=[Emoji.from_snake(emoji) for emoji in data.emojis],
            roles=roles,

            # booleans
            banner_animated=data.banner.is_animated() if data.banner else False,
        )
        return ret


class DashboardGuildPayload(AuthModel):
    guild_id: str


class BasePayloadWithGuildIdAndAuth(AuthModel):
    guild_id: str
