import disnake.utils
from disnake.ext import commands
from disnake.ext.commands import Cog, slash_command

from app import Bot, Embed, EmbedField
from app.decorators import db_required
from app.exceptions import BotException
from app.modals.items import CreateItemModal
from app.services.ItemService import ItemService
from app.types import CommandInteractionCommunity, CommandInteraction
from app.views import ConfirmationView, SendModalWithButtonView


class ItemsManagement(Cog, ItemService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="item",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def item(self, inter: CommandInteraction):
        pass

    @item.sub_command(
        name="create",
    )
    @db_required
    async def create_item_command(
        self,
        inter: CommandInteractionCommunity,
        title: str,
    ):
        has, items_count = await self.has_max_items(inter.guild)

        if has:
            raise BotException(
                400,
                f"Current guild has reached max items count, cannot create a new one. ",
                "Max items count reached",
            )

        modal = CreateItemModal(self.bot, title)
        view = SendModalWithButtonView(
            modal,
            button_label="Start creating",
            button_style=disnake.ButtonStyle.green,
            bot=self.bot,
            user=inter.author,
        )

        embed = Embed(
            title="Create item",
            description="Click the button below to start creating an item",
            fields=[
                EmbedField(
                    name="Current title",
                    value=title[:100],
                )
            ],
            user=inter.author,
        )

        await inter.send(embed=embed.info, view=view, ephemeral=True)

    @item.sub_command(name="remove")
    @db_required
    async def delete_item_command(
        self,
        inter: CommandInteractionCommunity,
        item: str = commands.Param(
            name="item",
            description="Item that will be deleted.",
        ),
    ):
        item_db = await self.get_item_by_title(inter.guild, item)
        if item_db is None:
            raise BotException(500, f"Item with title `{item}` not found", title="Not found item")

        confirmation_embed = Embed(
            title="Confirmation",
            description=f"Are you sure you want to delete item `{item_db.title}`?\nThis action "
            f"cannot be undone.\n\n\nP.S. Item parameters are listed below.",
            user=inter.user,
        ).info

        item_embed = await self.item_to_embed(
            item_db,
            user=inter.user,
            title="Item parameters",
            desc="You can make sure, that it's the right item.",
        )

        view = ConfirmationView(bot=self.bot, user=inter.user)

        await inter.send(embeds=[confirmation_embed, item_embed.info], view=view)

        await view.wait()

        if view.answer:
            await self.delete_item(item_db.id)
            await inter.edit_original_response(
                embed=Embed(
                    title="Item deleted",
                    description=f"Item `{item_db.title}` has been deleted.",
                    user=inter.user,
                ).success,
                components=self.bot.get_cancel_button(inter.user),
            )
        else:
            await inter.edit_original_response(
                embed=Embed(
                    title="Item deletion cancelled",
                    description=f"Item `{item_db.title}` has not been deleted.",
                    user=inter.user,
                ).info,
                components=self.bot.get_cancel_button(inter.user),
            )

    @item.sub_command(name="retrieve")
    @db_required
    async def retrieve_item_command(
        self,
        inter: CommandInteractionCommunity,
        item: str = commands.Param(
            name="item",
            description="Item that will be retrieved.",
        ),
    ):
        item_db = await self.get_item_by_title(inter.guild, item)
        if item_db is None:
            raise BotException(500, f"Item with title `{item}` not found", title="Not found item")

        embed = await self.item_to_embed(item_db, user=inter.user)

        await inter.send(embed=embed.info, components=[self.bot.get_cancel_button(inter.author)])

    @item.sub_command(name="edit")
    @db_required
    async def edit_item_command(
        self,
        inter: CommandInteractionCommunity,
        item: str = commands.Param(
            name="item",
            description="Item that will be edited.",
        ),
        edit_title: str = commands.Param(
            name="edit_title",
            description="New title of the item.",
        ),
    ):
        await inter.send("Not implemented yet", ephemeral=True)
        # @todo: implement item edit command
        # Edit title is required, but should be optional sometimes

        # item_db = await self.get_item_by_title(inter.guild, item)
        # if item_db is None:
        #     raise BotException(500, f"Item with title `{item}` not found", title="Not found item")
        #
        # view = SendModalWithButtonView(
        #     EditItemModal(self.bot, item_db, edit_title), user=inter.user, bot=self.bot
        # )
        #
        # await inter.send(embed=Embed(title="Edit item", user=inter.user).info, view=view)

    @delete_item_command.autocomplete("item")
    @retrieve_item_command.autocomplete("item")
    @edit_item_command.autocomplete("item")
    async def item_delete_or_retrieve_or_edit_item_autocomplete(
        self, inter: CommandInteraction, item: str
    ):
        items, more_that_zero = await self.get_items_by_title(guild=inter.guild, title=item)

        if not more_that_zero:
            return []

        titles = [i.title[:100] or "#Not found item" for i in items]
        # @todo: Fix this shit
        # when there's two or more items with the same title, it will return the first of them
        # and it's not good

        # possible solution: add item id to the title

        return titles


def setup(bot: Bot):
    bot.add_cog(ItemsManagement(bot))
