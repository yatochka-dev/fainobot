import datetime

from pydantic import BaseModel

from app.types import CommandInteraction


class SlashCommandStats(BaseModel):

    interaction_id: str
    command_name: str
    guild_id: str
    user_id: str
    channel_id: str
    created_at: datetime.datetime

    @classmethod
    def from_interaction(cls, interaction: CommandInteraction) -> "SlashCommandStats":
        return cls(
            interaction_id=str(interaction.id),
            command_name=str(interaction.application_command.name),
            guild_id=str(interaction.guild.id),
            user_id=str(interaction.author.id),
            channel_id=str(interaction.channel.id),
            created_at=interaction.bot.now,
        )


