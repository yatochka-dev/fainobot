from disnake.ext import commands
from disnake.ext.commands import Cog, slash_command

from app import Bot, Embed
from app.decorators import db_required
from app.exceptions import BotException
from app.services.ItemService import ItemService
from app.services.MemberService import MemberService
from app.types import CommandInteraction, CommandInteractionCommunity
from app.views import PaginationView


class Shop(Cog, ItemService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="shop",
    )
    async def shop_main(self, inter: CommandInteraction):
        # await self.shop(
        #     inter=inter
        # )
        pass

    @shop_main.sub_command(
        name="list",
        description="List all items in the shop"
    )
    async def shop(
            self,
            inter: CommandInteraction,

    ):
        items = await self.get_items(
            inter.guild
        )

        if not len(items):  # No items

            raise BotException(
                code=404,
                message="This guild has no items",
                title="No items found"
            )

        fields = [
            Embed.create_field(
                name=f"`#{item.index}`",
                value=f"{item.title[:100]}"
            )
            for item in items
        ]

        embed = Embed(
            title="Shop",
            description="Here are all the items you can buy",
            user=inter.user,
        )

        pages = embed.paginate(
            fields=fields,
            max_size=6,
            emb_style="default"
        )

        view = PaginationView(
            bot=self.bot,
            user=inter.user,
            pages=pages,
        )

        await inter.send(
            embed=pages[0],
            view=view,
        )

    @shop_main.sub_command(
        name="buy",
        description="Buy an item from the shop"
    )
    @db_required
    async def shop_buy(
            self,
            inter: CommandInteractionCommunity,
            item: str = commands.Param(
                name="item",
                description="Item that you want to buy",
            ),
    ):
        item_db = await self.get_item_from_autocomplete(inter.guild, item)
        if item_db is None:
            raise BotException(500, f"Item `{item}` not found", title="Not found item")

        try:
            bought_item = await self.member_buy_item(
                member=inter.author,
                item=item_db,
            )
        except ValueError as e:

            err = str(e)
            if err == "not_enough_money":
                raise BotException(500, "You don't have enough money", title="Not enough money")

            elif err == "out_of_stock":
                raise BotException(500, "This item is out of stock", title="Out of stock")

            elif err == "not_available":
                raise BotException(500, "This item is not available", title="Not available")
            else:
                raise BotException(500, str(e), title="This item can't be bought")

        if bought_item is None:
            raise BotException(500, "Something went wrong", title="Error")

        await inter.send(
            embed=Embed(
                title="Item bought",
                description=f"You bought `#{bought_item.original.index}` "
                            f"{bought_item.original.title}" + "\n" + f"Use `/inventory` to see "
                                                                     f"your items",
                user=inter.author,
            ).success,
        )

    @shop_main.sub_command(
        name="view",
        description="View an item from the shop"
    )
    async def shop_view(
            self,
            inter: CommandInteraction,
            item: str = commands.Param(
                name="item",
                description="Item that you want to view",
            ),
    ):
        item_db = await self.get_item_from_autocomplete(inter.guild, item)
        if item_db is None:
            raise BotException(500, f"Item `{item}` not found", title="Not found item")

        await inter.send(
            embed=(await self.item_to_embed(item_db, inter.author, title="Item",
                                            desc=f"#{item_db.index} - {item_db.title}")).default,
        )

    @shop_buy.autocomplete("item")
    @shop_view.autocomplete("item")
    async def item_autocomplete(
            self, inter: CommandInteraction, item: str
    ):
        items, more_that_zero = await self.get_items_by_title(guild=inter.guild, title=item)

        if not more_that_zero:
            return []

        titles = [f"#{i.index} - {i.title}"[:100] or "#Not found item" for i in items]

        return titles

    @slash_command(
        name="inventory",
    )
    @db_required
    async def inventory(
            self,
            inter: CommandInteractionCommunity,
    ):
        items = await self.get_member_inventory(inter.member_db)

        if not len(items):  # No items

            raise BotException(
                code=404,
                message="You don't have any items",
                title="No items found"
            )

        fields = [
            Embed.create_field(
                name=f"`#{item.original.index}` - {item.original.title}"[:100],
                value=f"{item.original.description or '#'}"[:200]
            )
            for item in items
        ]

        embed = Embed(
            title="Inventory",
            description="Here are all the items you have",
            user=inter.user,
        )

        pages = embed.paginate(
            fields=fields,
            max_size=6,
            emb_style="default"
        )

        view = PaginationView(
            bot=self.bot,
            user=inter.user,
            pages=pages,
        )

        await inter.send(
            embed=pages[0],
            view=view,
        )

    @slash_command(
        name="use",
    )
    @db_required
    async def use(
        self,
        inter: CommandInteractionCommunity,
        item: str = commands.Param(
            name="item",
            description="Item that you want to use, from "
                        "your inventory",
        ),
    ):
        pass

    @use.autocomplete("item")
    async def use_autocomplete(
            self, inter: CommandInteraction, item: str
    ):
        items, more_that_zero = await self.get_items_by_title(guild=inter.guild, title=item)

        if not more_that_zero:
            return []

        titles = [f"#{i.index} - {i.title}"[:100] or "#Not found item" for i in items]

        return titles


def setup(bot: Bot):
    bot.add_cog(Shop(bot))
