from disnake.ext import commands
from disnake.ext.commands import Cog, slash_command

from app import Bot, Embed
from app.decorators import db_required
from app.exceptions import BotException
from app.services.ItemService import ItemService
from app.services.MemberService import MemberService
from app.translation.main import TranslationClient
from app.types import CommandInteraction, CommandInteractionCommunity
from app.views import PaginationView
from disnake import Interaction

client = TranslationClient.get_instance()

shop_init = client.get_command_init("shop")
list_init = client.get_command_init("shop_list")
buy_init = client.get_command_init("shop_buy")
view_init = client.get_command_init("shop_view")

class Shop(Cog, ItemService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name=shop_init.name,
    )
    async def shop_main(self, inter: CommandInteraction):
        pass

    @shop_main.sub_command(
        name=list_init.name,
        description=list_init.description
    )
    async def shop(
            self,
            inter: CommandInteraction,
    ):
        _ = await self.bot.i10n.get_command_translation(inter)

        items = await self.get_items(
            inter.guild
        )

        if not len(items):  # No items

            raise BotException(
                code=404,
                message=_.get_error("no_items"),
                title=_.get_error("title")
            )

        fields = [
            Embed.create_field(
                name=f"`#{item.index}`",
                value=f"{item.title[:100]}"
            )
            for item in items
        ]

        embed = Embed(
            title=_["title"],
            description=_["description"],
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
        name=buy_init.name,
        description=buy_init.description
    )
    @db_required
    async def shop_buy(
            self,
            inter: CommandInteractionCommunity,
            item: str = commands.Param(
                name=buy_init.options["item"].name,
                description=buy_init.options["item"].description
            ),
    ):

        _ = await self.bot.i10n.get_command_translation(inter)
        item_db = await self.get_item_from_autocomplete(inter.guild, item)
        if item_db is None:
            raise BotException(500, _.get_error('no_item').apply(item=item), title=_.get_error("title"))

        try:
            bought_item = await self.member_buy_item(
                member=inter.author,
                item=item_db,
            )
        except ValueError as e:

            err = str(e)
            if err == "not_enough_money":
                raise BotException(500, _["not_enough"], title=_.get_error("title"))

            elif err == "out_of_stock":
                raise BotException(500, _["out_of_stock"], title=_.get_error("title"))

            elif err == "not_available":
                raise BotException(500, _["not_available"], title=_.get_error("title"))
            else:
                raise BotException(500, str(e), title=_.get_error("title"))

        if bought_item is None:
            raise BotException(500, _["went_wrong"], title=_.get_error("title"))

        await inter.send(
            embed=Embed(
                title=_["success_title"],
                description=_["success"].apply(
                    index=item_db.index,
                    title=item_db.title,
                ),
                user=inter.author,
            ).success,
        )

    @shop_main.sub_command(
        name=view_init.name,
        description=view_init.description
    )
    async def shop_view(
            self,
            inter: CommandInteraction,
            item: str = commands.Param(
                name=view_init.options["item"].name,
                description=view_init.options["item"].description,
            ),
    ):
        _ = await self.bot.i10n.get_command_translation(inter)
        item_db = await self.get_item_from_autocomplete(inter.guild, item)
        if item_db is None:
            raise BotException(500, _.get_error('no_item').apply(item=item), title=_.get_error("title"))

        await inter.send(
            embed=(await self.item_to_embed(item_db, inter.author, title=_['title'],
                                            desc=_["description"].apply(
                                                index=item_db.index,
                                                title=item_db.title,
                                            ))).default,
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
