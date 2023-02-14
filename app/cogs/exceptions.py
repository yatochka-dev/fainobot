from disnake.ext.commands import Cog

from app import Bot
from app.exceptions import BotException, CommandInvokeError
from app.types import CommandInteraction


class ExceptionsHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener(name="on_slash_command_error")
    @Cog.listener(name="on_message_command_error")
    async def interaction_commands_error_handler(
        self, inter: CommandInteraction, error: Exception
    ) -> None:
        if isinstance(error, BotException):
            await inter.send(
                embed=error.to_embed(inter.author),
                ephemeral=True,
                delete_after=180,
            )
        else:
            message = str(error)

            if isinstance(error, CommandInvokeError):
                message = str(error.original)

            await inter.send(
                embed=BotException(500, message).to_embed(inter.author),
                ephemeral=True,
                delete_after=180,
            )
            self.bot.logger.error("Unhandled exception")
            raise error

def setup(bot: Bot):
    bot.add_cog(ExceptionsHandler(bot))
