import disnake.utils
from disnake import ModalInteraction
from disnake.ext.commands import Cog, slash_command

from app import Bot, EmbedField, Embed
from app.dantic import ValidItemDataDANT
from app.decorators import db_required
from app.exceptions import BotException
from app.services.ItemService import ItemService
from app.types import CommandInteractionCommunity
from app.utils.datendtime import parse_datetime


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

        fields = [
            EmbedField(name="Title", value=item.title, inline=False),
            EmbedField(name="Price", value=item.price, inline=False),
            EmbedField(name="Description", value=item.description or "#", inline=False),
            EmbedField(name="Reply", value=item.replyMessage or "#", inline=False),
            EmbedField(name="Stock", value=item.stock or "#", inline=False),
        ]
        if item.availableUntil:
            fields.append(
                EmbedField(
                    name="Available until",
                    value=f"{disnake.utils.format_dt(item.availableUntil)}",
                    inline=False,
                )
            )

        embed = Embed(
            title="Item created",
            description=f"Item with id `{item.id}` has been created.",
            fields=fields,
            user=interaction.author,
        ).success

        await interaction.send(embed=embed, components=self.bot.get_cancel_button(interaction.user))


class ItemsManagement(Cog, ItemService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="create_item",
        default_member_permissions=disnake.Permissions(administrator=True),
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


def setup(bot: Bot):
    bot.add_cog(ItemsManagement(bot))
