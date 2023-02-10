import disnake
from fastapi import APIRouter, Depends
from prisma import models

from app import Bot, get_bot_from_request

router = APIRouter(
    prefix="/status",
)


@router.get("/")
async def status(bot: Bot = Depends(get_bot_from_request)):
    # get all online users
    servers = len(bot.guilds)
    online_users = sum(1 for m in bot.get_all_members() if m.status != disnake.Status.offline)
    channels = {
        "text": sum(1 for c in bot.get_all_channels() if isinstance(c, disnake.TextChannel)),
        "voice": sum(1 for c in bot.get_all_channels() if isinstance(c, disnake.VoiceChannel)),
        "other": sum(1 for c in bot.get_all_channels() if not isinstance(c, (disnake.TextChannel, disnake.VoiceChannel))),
    }
    # voice_connections = len(bot.voice_clients)

    total_commands_invoked: list[models.InvokedCommand] = await bot.prisma.invokedcommand.find_many()

    invocations = [
        cmd.count for cmd in total_commands_invoked
    ]

    summarized = sum(invocations)

    return {
        "servers": servers,
        "online_users": online_users,
        "total_commands_invoked": summarized,
        "channels": channels,
        "verbose_invocations": [
            {cmd.name: cmd.count} for cmd in total_commands_invoked
        ]
    }
