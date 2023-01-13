from enum import Enum
from typing import SupportsInt, Union

import disnake
from disnake import ApplicationCommandInteraction
from prisma import models

# CommandInteraction type is used for slash commands
#
# Example:
# async def <SLASH_CMD_NAME>(self, interaction: CommandInteraction) -> None:
CommandInteraction = ApplicationCommandInteraction

DiscordUtilizer = disnake.ClientUser | disnake.Member | disnake.User

SupportsIntCast = Union[SupportsInt, str, bytes, bytearray]


# ... you can add your custom types and enums here

class CommandInteractionUserAndGuild(CommandInteraction):
    user_db: models.User
    guild_db: models.Guild


class CommandInteractionCommunity(CommandInteractionUserAndGuild):
    member_db: models.Member


class CacheNamespaces(Enum):

    # member cool-downs
    member_voice_cooldown = "member_voice_cooldown"
    member_message_cooldown = "member_message_cooldown"
    member_reaction_cooldown = "member_reaction_cooldown"


