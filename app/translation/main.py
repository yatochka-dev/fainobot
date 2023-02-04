import asyncio
import typing

import disnake

from app.types import CacheNamespaces, CommandInteraction
from .core import TranslationsManager

if typing.TYPE_CHECKING:
    from app import Bot


def split_key(key: str, splitters: list[str]) -> tuple[str, str]:
    for splitter in splitters:
        if splitter in key:
            dt = key.split(splitter)
            if len(dt) == 2:
                return dt[0], dt[1]
            else:
                raise ValueError(f"Invalid key: {key}")
    raise ValueError(f"Invalid key: {key}")


TypesToGetGuildId = int | str | disnake.Guild | CommandInteraction


class TranslationState:
    def __init__(
            self,
            language: str,
            group: str,
            client: "TranslationClient" = None,
    ):
        self.language = language
        self.group = group
        self.client = client

    def __call__(self, *args, **kwargs):
        return self.__class__(self.language, self.group)

    def __getitem__(self, item):
        return self._(item)

    def _(self, key: str):
        return self.client.get_translation(f"{self.group}:{key}", lang=self.language)


class TranslationClient:
    def __init__(
            self,
            languages: list[str],
            dir_path: str,
            default_lang: str = "en",
            splitters=None,
            bot: "Bot" = None,
    ):
        if splitters is None:
            splitters = [":"]
        self.languages = languages
        self.dir_path = dir_path
        self.default_lang = default_lang
        self.splitters = splitters
        self.bot = bot

        self.manager = TranslationsManager(
            languages=["en", "ru", "uk"],
            dir_path="P:\PyCharm\Projects\\fainobot\\translations",
        )
        self.processed_data = self.manager.process_translations()

    @staticmethod
    def _get_guild_snowflake(value: TypesToGetGuildId) -> str:
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        elif isinstance(value, disnake.Guild):
            return str(value.id)
        elif isinstance(value, CommandInteraction):
            return str(value.guild_id)

    def get_translation(
            self,
            __key: str,
            lang: str = None,
    ):
        if not lang:
            lang = self.default_lang

        group, key = split_key(__key, splitters=self.splitters)

        return self.processed_data.get_language(lang).get_group(group).get_string(key)

    async def get_translation_async(
            self,
            __key: str,
            lang: str = None,
            payload: TypesToGetGuildId = None
    ):
        if payload:
            lang = await self.get_language_from_interaction(payload)
        elif not lang:
            lang = self.default_lang

        group, key = split_key(__key, splitters=self.splitters)

        return self.processed_data.get_language(lang).get_group(group).get_string(key)

    async def create_translation_state(
            self,
            *,
            lang: str = None, group: str = None,
            payload: disnake.CommandInteraction = None
    ):
        if payload:
            lang = await self.get_language_from_interaction(payload)
        elif not lang:
            lang = self.default_lang

        self.bot.logger.debug(f"Creating translation state for {lang} language")

        return TranslationState(
            language=lang or self.default_lang,
            group=group,
            client=self,
        )

    def __getitem__(
            self,
            __key: str,
            lang: str = None,
    ):
        return self.get_translation(__key, lang)

    async def get_language_from_interaction(self, payload: TypesToGetGuildId):
        snowflake = self._get_guild_snowflake(payload)

        self.bot.logger.debug(f"Getting language for {snowflake} guild")

        lang = await self.bot.cache.get(
            key=f"{snowflake}",
            namespace=CacheNamespaces.guilds_cached_language.value,
        )

        self.bot.logger.debug(f"Got language {lang} for {snowflake} guild from cache")

        if not lang:
            if snowflake:
                guild = await self.bot.prisma.guild.find_unique(
                    where={"snowflake": snowflake}
                )
                lang = guild.language
                await self.bot.cache.set(
                    key=f"{snowflake}",
                    value=lang,
                    namespace=CacheNamespaces.guilds_cached_language.value,
                    # for 2 minutes
                    ttl=120,
                )
            else:
                lang = self.default_lang

        return lang


async def main():
    client = TranslationClient(
        languages=["en", "ru", "uk"],
        dir_path="P:\PyCharm\Projects\\fainobot\\translations",
        default_lang="uk",
        splitters=(
            ":",
            ".",
        ),
    )

    _ = await client.create_translation_state(group="commands", lang="uk")

    string = _["welcome"]
    print(string)


if __name__ == "__main__":
    asyncio.run(main())
