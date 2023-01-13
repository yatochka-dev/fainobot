from disnake.ext.commands import Cog, slash_command

from app import Bot, md, EmbedField
from app.decorators import db_required
from app.embedding import Embed
from app.services.GuildService import GuildService
from app.types import CommandInteraction, CommandInteractionCommunity
from app.utils.embeds import create_embeds_from_fields
from app.views import PaginationView


class Command(Cog, GuildService):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command()
    async def test_cache(self, inter: CommandInteraction):
        pass

    @test_cache.sub_command(
        name="set"
    )
    async def set_cache(self, inter: CommandInteraction, k: str, v: str, ttl: int):
        await self.bot.cache.set(k, v, ttl=ttl)
        await inter.send(
            f"{await self.bot.cache.get(k)}"
        )

    @test_cache.sub_command(
        name="get"
    )
    async def get_cache(self, inter: CommandInteraction, k: str):
        await inter.send(
            f"{await self.bot.cache.get(k)}"
        )

    @slash_command()
    @db_required
    async def ping(self, inter: CommandInteractionCommunity) -> None:
        print("Ping command")
        await inter.response.defer()
        current_latency = round(self.bot.latency * 1000, 2)

        match current_latency:
            case x if x <= 50:
                color = (0, 255, 0)

            case x if x <= 100:
                color = (255, 255, 0)

            case x if x <= 150:
                color = (255, 165, 0)

            case x if x <= 200:
                color = (255, 0, 0)

            case _:
                color = (0, 0, 0)

        await inter.send(
            embed=Embed(
                title="Pong!",
                description=f"{md('Latency'):bold}:{current_latency}ms",
                user=inter.user,
            ).as_color(color)
        )

    @slash_command()
    async def guilds(self, inter: CommandInteraction) -> None:

        guilds = await self.get_all_guilds()

        fields = [
            EmbedField(name=f"#{i}", value=f"{guild.snowflake}")
            for i, guild in enumerate(guilds, 1)
        ]

        embed = Embed(
            title="Guilds",
            description=f"{md('Guilds'):bold}: {len(guilds)}",
            user=inter.user,
        )

        embeds = create_embeds_from_fields(
            embed, fields, max_size=1,
        )

        view = PaginationView(
            bot=self.bot, user=inter.user, pages=embeds
        )

        await inter.send(
            embed=embeds[0],
            view=view
        )


def setup(bot: Bot):
    bot.add_cog(Command(bot))
