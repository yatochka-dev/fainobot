from disnake.ext.commands import Cog, is_owner, slash_command

from app import Bot, Settings, Embed
from app.services.cache.CacheService import CacheService
from app.types import CommandInteraction
from app.views import PaginationView


class Admin(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @is_owner()
    @slash_command(
        guild_ids=Settings.TESTING_GUILDS
    )
    async def cache(
            self, inter: CommandInteraction, func: str,
            key: str = None, value: str = None, namespace: str = None, ttl: int = None
    ):
        service = CacheService.set_bot(self.bot)

        func = getattr(service, func)

        if not func:
            return await inter.send("Invalid function")

        kwargs = {}

        if key:
            kwargs["key"] = key

        if value:
            kwargs["value"] = value

        if namespace:
            kwargs["namespace"] = namespace

        if ttl:
            kwargs["ttl"] = ttl

        result = await func(**kwargs)

        await inter.send(f"Result: {result}")

    @is_owner()
    @slash_command(
        guild_ids=Settings.TESTING_GUILDS,
        name="guilds",
    )
    async def guilds(self, inter: CommandInteraction):
        pass

    @is_owner()
    @guilds.sub_command(
        name="list",
        description="List all guilds the bot is in"
    )
    async def guilds_list(self, inter: CommandInteraction):
        guilds = self.bot.guilds

        fields = [
            Embed.create_field(
                name=guild.name,
                value=f"ID: {guild.id}\nOwner: {guild.owner} ({guild.id})\nMembers: "
                      f"{guild.member_count}",
                inline=True
            )
            for guild in guilds
        ]

        embed = Embed(
            user=inter.author,
            title="Guilds List",
        )
        embeds = embed.paginate(
            fields=fields,
            max_size=15,
            emb_style="default"
        )

        view = PaginationView(
            pages=embeds,
            user=inter.author,
            bot=self.bot,
            timeout=60,
        )

        await inter.send(embed=embeds[0], view=view)

    @is_owner()
    @guilds.sub_command(
        guild_ids=Settings.TESTING_GUILDS,
        name="leave",
    )
    async def leave_guild(self, inter: CommandInteraction, snowflake: str):
        guild = self.bot.get_guild(int(snowflake))

        if not guild:
            return await inter.send("Guild not found")

        await guild.leave()

        await inter.send(f"Left guild {guild.name} ({guild.id}) ({guild.member_count})",
                         components=self.bot.get_cancel_button(user=inter.author))

    @is_owner()
    @slash_command(
        guild_ids=Settings.TESTING_GUILDS,
        name="add_money",
    )
    async def add_money(self, inter: CommandInteraction, amount: int, user: str):

        data = await self.bot.prisma.member.update(
            where={
                "id": int(user)
            },
            data={
                "money": {
                    "increment": amount
                }
            }
        )
        await inter.send(f"Added {amount} to {user!r} ({data.money})")



def setup(bot: Bot):
    bot.add_cog(Admin(bot))
