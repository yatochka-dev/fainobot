import disnake
from disnake import VoiceChannel
from disnake.components import MessageComponent
from disnake.ext.commands import Cog

from app import Embed


class LowLevelListener(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_button_click")
    async def on_cancel_button(self, inter: disnake.MessageInteraction):
        component: MessageComponent = inter.component

        if isinstance(inter.channel, VoiceChannel):
            return

        if not component.custom_id.startswith("deleteOriginalMessage"):
            return

        _, user_id = component.custom_id.split("_")

        manage_msgs = inter.channel.permissions_for(inter.author).manage_messages

        self.bot.logger.debug(f"manage_msgs: {manage_msgs}")
        self.bot.logger.debug(f"inter.author.id: {inter.author.id}")
        self.bot.logger.debug(f"user_id: {user_id}")

        can_delete = manage_msgs or int(user_id) == inter.author.id

        self.bot.logger.debug(f"can_delete: {can_delete}")

        if not can_delete:
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
            # await inter.message.edit(
            #     embed=Embed(
            #         title="Message deleted!",
            #         description=f"The message was deleted successfully, by <@!{user_id}>.",
            #         user=inter.author,
            #     ).success,
            #     delete_after=3,
            #     view=None,
            # )
            await inter.message.delete(delay=1)

        except disnake.NotFound:
            # original_message = await inter.original_response()
            # await original_message.delete()

            await inter.send(
                embed=Embed(
                    title="Can't delete message!",
                    description="This message is ephemeral or something went wrong.",
                    user=inter.author,
                ).error,
                ephemeral=True,
                delete_after=15,
            )


def setup(bot):
    bot.add_cog(LowLevelListener(bot))
