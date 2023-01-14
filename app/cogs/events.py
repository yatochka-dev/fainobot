import os

import disnake
from disnake.components import MessageComponent
from disnake.ext.commands import Cog

from app import Bot, Embed, md, cb
from app.exceptions import BotException
from app.services.GuildService import GuildService
from app.services.MemberService import MemberService
from app.types import CommandInteraction


class Events(Cog, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def get_channel(guild: disnake.Guild):
        for channel in guild.channels:
            if isinstance(channel, disnake.TextChannel):
                can_send = channel.permissions_for(guild.me).send_messages
                if can_send:
                    return channel
                else:
                    continue

    @Cog.listener(
        "on_ready",
    )
    async def is_ready(self):
        self.bot.logger.info(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
        self.bot.logger.info(f"Started bot in {os.getenv('STATE_NAME').title()} mode.")
        self.bot.logger.info("------")

        await self.bot.cache.set("start_time", self.bot.now.timestamp())

        for guild in self.bot.guilds:
            if not await self.exists_guild(guild.id):
                await self.add_guild(guild)
                self.bot.logger.info(f"Added guild: {guild.name} (ID: {guild.id})")
            else:
                self.bot.logger.info(f"Guild already exists: {guild.name} (ID: {guild.id})")

    @Cog.listener(
        "on_guild_join",
    )
    async def joined_guild(self, guild: disnake.Guild):
        await self.add_guild(guild)
        self.bot.logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")

        embed = Embed(
            title="Thanks for adding me!",
            description=f"I'm a template bot for {md('Disnake'):bold}."
                        f"\n"
                        f"{cb(f'Start-Process -FilePath {self.bot.APP_SETTINGS.github_link}'):bash}",
            user=guild.me,
        ).info

        channel = await self.get_channel(guild)

        if channel:
            await channel.send(embed=embed)
            await guild.owner.send(embed=embed)
        else:
            await guild.owner.send(embed=embed)

    @Cog.listener(
        "on_guild_remove",
    )
    async def quit_guild(self, guild):
        await self.remove_guild(guild)
        self.bot.logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

    @Cog.listener(
        "on_member_remove",
    )
    async def member_left(self, member: disnake.Member):
        await self.remove_member(member, ignore_not_found=True)
        self.bot.logger.info(f"Member left: {member} (ID: {member.id})")


class ExceptionsHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_slash_command_error(self, inter: CommandInteraction, error: Exception) -> None:
        if isinstance(error, BotException):
            await inter.send(
                embed=error.to_embed(inter.author),
                ephemeral=True,
                delete_after=180,
                components=[self.bot.get_cancel_button(inter.author)],
            )
        else:
            await inter.send(
                embed=BotException(500, str(error)).to_embed(inter.author),
                ephemeral=True,
                delete_after=180,
                components=[self.bot.get_cancel_button(inter.author)],
            )
            self.bot.logger.error("Unhandled exception", exc_info=error)
            raise error


class LowLevelListener(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_button_click")
    async def on_cancel_button(self, inter: disnake.MessageInteraction):
        component: MessageComponent = inter.component

        if not component.custom_id.startswith("deleteOriginalMessage"):
            return

        _, user_id = component.custom_id.split("_")

        if int(user_id) != inter.author.id:
            await inter.send(
                embed=Embed(
                    title="You are not allowed to do this!",
                    description="You are not allowed to delete this message.",
                    user=inter.author,
                ).error,
                ephemeral=True,
                delete_after=15,
            )
            return

        try:
            await inter.message.edit(
                embed=Embed(
                    title="Message deleted!",
                    description=f"The message was deleted successfully, by <@!{user_id}>.",
                    user=inter.author,
                ).success,
                delete_after=3,
                view=None,
            )
        except disnake.NotFound:
            await inter.send(
                embed=Embed(
                    title="Can't delete message!",
                    description="This message is ephemeral or something went wrong.",
                    user=inter.author,
                ).error,
                ephemeral=True,
                delete_after=15,
            )


def setup(bot: Bot):
    bot.add_cog(Events(bot))
    bot.add_cog(ExceptionsHandler(bot))
    bot.add_cog(LowLevelListener(bot))
