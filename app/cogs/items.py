import disnake.utils
from disnake import ModalInteraction
from disnake.ext import commands
from disnake.ext.commands import Cog, slash_command

from app import Bot, Embed
from app.dantic import ValidItemDataDANT
from app.decorators import db_required
from app.exceptions import BotException
from app.services.ItemService import ItemService
from app.types import CommandInteractionCommunity, CommandInteraction
from app.utils.datendtime import parse_datetime
from app.views import ConfirmationView


class CreateItemModal(disnake.ui.Modal):
    def __init__(self, bot: Bot, title: str):
        self.title_ = title
        components = [
            disnake.ui.TextInput(
                label="Item price",
                placeholder="100",
                value="100",
                custom_id="price",
                min_length=1,
                max_length=7,
            ),
            disnake.ui.TextInput(
                label="Item stock",
                placeholder="100",
                custom_id="stock",
                min_length=1,
                max_length=4,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Available until",
                placeholder="5d10h30m",
                custom_id="available_time",
                min_length=1,
                max_length=20,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Item description",
                placeholder="This item is cool",
                custom_id="description",
                min_length=0,
                max_length=1024,
                style=disnake.TextInputStyle.multi_line,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Item reply",
                placeholder="Thanks for buying this item!",
                custom_id="reply",
                min_length=0,
                max_length=1024,
                style=disnake.TextInputStyle.multi_line,
                required=False,
            ),
        ]
        self.bot = bot
        super().__init__(title="Create item", components=components)

    async def callback(self, interaction: ModalInteraction, /) -> None:
        title = self.title_
        description = (
            interaction.text_values["description"]
            if len(interaction.text_values["description"]) > 0
            else None
        )
        reply = (
            interaction.text_values["reply"] if len(interaction.text_values["reply"]) > 0 else None
        )

        price_raw = interaction.text_values["price"]
        if price_raw.isdigit():
            price = int(price_raw)
        else:
            await interaction.response.send_message("Price must be a number", ephemeral=True)
            return

        stock_raw = interaction.text_values["stock"]
        if stock_raw:
            if stock_raw.is_digit():
                stock = int(stock_raw)
            else:
                await interaction.response.send_message("Stock must be a number", ephemeral=True)
                return
        else:
            stock = None

        if interaction.text_values["available_time"]:
            try:
                available_time = parse_datetime(interaction.text_values["available_time"])
            except ValueError:
                await interaction.response.send_message(
                    f"Available time must be a valid time, not "
                    f"{interaction.text_values['available_time']}",
                    ephemeral=True,
                )
                return
        else:
            available_time = None

        data = ValidItemDataDANT(
            title=title,
            price=price,
            stock=stock,
            available_time=available_time,
            description=description,
            reply=reply,
        )

        service = ItemService.set_bot(self.bot)

        try:
            item = await service.create_item(data, interaction.guild)
        except ValueError as e:
            exc = BotException(500, str(e), "Item creation failed")
            await interaction.send(exc.to_embed(interaction.user), ephemeral=True)
            return

        embed = await service.item_to_embed(
            item,
            user=interaction.author,
            title="Item created",
            desc="Item with id `{item.id}` has been created.",
        )

        await interaction.send(
            embed=embed.info, components=self.bot.get_cancel_button(interaction.user)
        )


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

        await inter.response.send_modal(CreateItemModal(self.bot, title))

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

    @delete_item_command.autocomplete("item")
    @retrieve_item_command.autocomplete("item")
    async def item_delete_item_autocomplete(self, inter: CommandInteraction, item: str):
        items, more_that_zero = await self.get_items_by_title(guild=inter.guild, title=item)

        if not more_that_zero:
            return []

        titles = [i.title[:100] or "#Not found item" for i in items]
        return titles


def setup(bot: Bot):
    bot.add_cog(ItemsManagement(bot))
