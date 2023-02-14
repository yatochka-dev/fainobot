import disnake
from disnake import MessageInteraction
from disnake.ui import Item, View

from app.exceptions import BotException
from app.types import DiscordUtilizer
from .bot import Bot
from .embedding import Embed


class BaseView(View):

    def __init__(self, bot: Bot, user: DiscordUtilizer, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.bot = bot

    async def interaction_check(self, interaction: MessageInteraction):
        """

            Exception codes:
                1 - Forbidden
                2 - Not found
        """
        BotException.assert_value(
            not interaction.user.bot, error_code=403, message="This interaction can be used by bots"
        )

        BotException.assert_value(
            interaction.user.id == self.user.id, error_code=403,
            message="You can't use this interaction"
        )
        return True

    async def on_error(self, error: Exception, item: Item, interaction: MessageInteraction) -> None:
        if isinstance(error, BotException):

            await interaction.send(embed=error.to_embed(user=interaction.user), ephemeral=True)
        else:
            await interaction.response.send_message("An unknown error occured.", ephemeral=True)
            raise error


class PaginationView(BaseView):

    def __init__(
            self,
            bot: Bot,
            user: DiscordUtilizer,
            pages: list[Embed],
            **kwargs,
    ):
        super().__init__(bot, user, **kwargs)
        self.pages = pages
        self.current_page = 0

        self._update_state()

    def _update_state(self) -> None:
        if len(self.pages) == 1:
            self.clear_items()
            self.add_item(self.remove)

        self.first_page.disabled = self.prev_page.disabled = self.current_page == 0
        self.last_page.disabled = self.next_page.disabled = self.current_page == len(self.pages) - 1

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
    async def first_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.current_page = 0
        self._update_state()

        await inter.response.edit_message(embed=self.pages[self.current_page], view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.current_page -= 1
        self._update_state()

        await inter.response.edit_message(embed=self.pages[self.current_page], view=self)

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red, custom_id="delete")
    async def remove(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=None)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.current_page += 1
        self._update_state()

        await inter.response.edit_message(embed=self.pages[self.current_page], view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.current_page = len(self.pages) - 1
        self._update_state()

        await inter.response.edit_message(embed=self.pages[self.current_page], view=self)


class CancelView(BaseView):

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red, custom_id="delete")
    async def remove(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.delete_original_message()


class ConfirmationView(BaseView):
    answer: bool = False

    @disnake.ui.button(emoji="✅", style=disnake.ButtonStyle.green, custom_id="confirm")
    async def confirm(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.answer = True
        await inter.response.defer()
        self.stop()

    @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.red, custom_id="cancel")
    async def cancel(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.answer = False
        await inter.response.defer()
        self.stop()


class SendModalWithButtonView(BaseView):

    def __init__(
            self,
            modal: disnake.ui.Modal,
            button_label: str = "Open modal",
            button_style: disnake.ButtonStyle = disnake.ButtonStyle.blurple,
            button_emoji: str = None,
            include_cancel_button: bool = False,
            **kwargs,
    ):
        self.modal = modal

        self.button_label = button_label
        self.button_style = button_style
        self.button_emoji = button_emoji
        self.include_cancel_button = include_cancel_button
        super().__init__(**kwargs)

        self._update_state()

    def _update_state(self) -> None:

        if not self.include_cancel_button:
            self.remove_item(self.remove)

        for item in self.children:
            if isinstance(item, disnake.ui.Button) and item.custom_id == "send":
                item.emoji = self.button_emoji
                item.label = self.button_label
                item.style = self.button_style

    @disnake.ui.button(emoji="📩", style=disnake.ButtonStyle.blurple, custom_id="send")
    async def send(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(self.modal)
        await inter.edit_original_response(view=None)
        self.stop()

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red, custom_id="delete")
    async def remove(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        await inter.delete_original_message()
        self.stop()


class MembersView(PaginationView):

    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(**kwargs)

    def _update_state(self) -> None:
        if len(self.pages) == 1:
            self.clear_items()
            self.add_item(self.remove)
            self.add_item(self.reveal)

        self.first_page.disabled = self.prev_page.disabled = self.current_page == 0
        self.last_page.disabled = self.next_page.disabled = self.current_page == len(self.pages) - 1

    @staticmethod
    def _get_members(message: disnake.Message) -> list[disnake.Member]:
        embed = message.embeds[0]

        mentions = []

        for f in embed.fields:
            id_ = int(f.name)
            member = message.guild.get_member(id_)
            if member:
                mentions.append(member)

        return mentions

    @disnake.ui.button(label="reveal️", style=disnake.ButtonStyle.blurple, custom_id="reveal")
    async def reveal(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction):
        original_message = await inter.channel.fetch_message(inter.message.id)

        members = self._get_members(original_message)

        if not members:
            return await inter.response.send_message("No members found", ephemeral=True)

        text = ",\n".join([f"{member.mention} ({member.id})" for member in members])
        await inter.send(text, ephemeral=True)
