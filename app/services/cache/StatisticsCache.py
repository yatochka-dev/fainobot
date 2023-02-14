import time

from .CacheService import CacheService
from ...types import CacheNamespaces, CommandInteraction


class StatisticsCacheService(CacheService):
    namespace: str = CacheNamespaces.invoked_commands.value
    invoked_names: set[str] = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def command_invoked(
            self,
            dt: CommandInteraction,
    ):

        cache_key = f"{dt.application_command.qualified_name}"
        cache_key = cache_key.replace(" ", "_")
        cache_key = cache_key.lower()

        exists = await self.exists(cache_key, namespace=self.namespace)

        if exists:
            await self.increment(cache_key, namespace=self.namespace, amount=1)
        else:
            await self.set(cache_key, 1, namespace=self.namespace)

        self.invoked_names.add(cache_key)

    async def get_data(self):
        data: list[int] = await self.get_many(
            list(self.invoked_names),
            namespace=self.namespace,
        )

        # I have a list of command names
        # I have a list of integers
        # I want to get a dict of command names and integers

        if not data:
            return

        return dict(zip(self.invoked_names, data))

    @staticmethod
    def data_to_db_standards(data: dict[str, int]):

        # {"profile": 1, "help": 2, "ping": 3} -> {"profile": {"increment": 1}, "help": {
        # "increment": 2}, "ping": {"increment": 3}

        if not data:
            return

        new_data = {
            k: {"increment": v} for k, v in data.items()
        }

        return new_data

    async def save_to_db(self):
        start = time.perf_counter()
        data = await self.get_data()

        if not data:
            return

        data = self.data_to_db_standards(data)

        for command_name, data in data.items():
            self.invoked_names.remove(command_name)
            await self.bot.prisma.invokedcommand.upsert(
                where={
                    "name": command_name,
                },
                data={
                    "update": {
                        "count": data,
                    },
                    "create": {
                        "name": command_name,
                        "count": data.get("increment", 0),
                    }
                },
            )



        end = time.perf_counter()
        await self.clear(namespace=self.namespace)
        self.bot.logger.info(f"Saved invoked commands to db in {end - start} seconds")

    async def clear_data(self):
        pass
