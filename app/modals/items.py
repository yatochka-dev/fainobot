import disnake.ui
from disnake import ModalInteraction
from prisma import models

from app import Bot, Embed
from app.dantic import ValidItemDataDANT
from app.exceptions import BotException
from app.services.ItemService import ItemService
from app.utils.datendtime import parse_datetime, format_datetime
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


class EditItemModal(disnake.ui.Modal):
    def __init__(self, bot: Bot, item: models.Item, title: str):
        self.title_ = title
        self.item = item
        components = [
            disnake.ui.TextInput(
                label="Item price",
                placeholder="100",
                value=str(item.price) or "100",
                custom_id="price",
                min_length=1,
                max_length=7,
            ),
            disnake.ui.TextInput(
                label="Item stock",
                placeholder="100",
                value=str(item.stock) if item.stock else None,
                custom_id="stock",
                min_length=1,
                max_length=4,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Available until",
                placeholder="5d10h30m",
                custom_id="available_time",
                value=str(format_datetime(item.availableUntil)) if item.availableUntil else None,
                min_length=1,
                max_length=20,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Item description",
                placeholder="This item is cool",
                custom_id="description",
                value=item.description or "",
                min_length=0,
                max_length=1024,
                style=disnake.TextInputStyle.multi_line,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Item reply",
                placeholder="Thanks for buying this item!",
                custom_id="reply",
                value=item.replyMessage or "",
                min_length=0,
                max_length=1024,
                style=disnake.TextInputStyle.multi_line,
                required=False,
            ),
        ]
        self.bot = bot
        super().__init__(title="Edit item", components=components)

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
            if stock_raw.isdigit():
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

        view = ConfirmationView(self.bot, user=interaction.user)
        item_embed = await service.item_to_embed(
            self.item,
            user=interaction.user,
            title="Confirm item edit",
            desc="Are you sure you want to edit this item?",
        )

        await interaction.send(
            embed=item_embed.info,
            view=view,
        )

        await view.wait()

        if not view.answer:
            await interaction.edit_original_response(
                embed=Embed(
                    title="Item edit cancelled",
                    description=f"Item `{self.item.title}` won't be updated.",
                    user=interaction.user,
                ).info,
                components=self.bot.get_cancel_button(interaction.user),
            )
        else:
            try:
                item = await service.update_item(item_id=self.item.id, data=data)
            except ValueError as e:
                exc = BotException(500, str(e), "Item edit failed")
                await interaction.send(exc.to_embed(interaction.user), ephemeral=True)
            else:
                item = await service.get_item(item.id, interaction.guild)
                embed = await service.item_to_embed(
                    item,
                    user=interaction.user,
                    title="Item edited",
                    desc="Item with id `{item.id}` has been edited.",
                )
                await interaction.edit_original_response(
                    embed=embed.info, components=self.bot.get_cancel_button(interaction.user)
                )
