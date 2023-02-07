import dataclasses
import json
import os
from pathlib import Path
from string import Template
from typing import NamedTuple

from disnake import Localized
from pydantic import BaseModel


# TranslationFile = NamedTuple('TranslationFile', "path, group, lang")
# create as class

class Option(BaseModel):
    name: str
    description: str


class Command(BaseModel):
    """
     "profile_cmd": {
    "name": "profile",
    "description": "Get a member's profile",
    "options": {
      "user": {
        "name": "user",
        "description": "The member to get the profile of"
      }
    },
    "strings": {
      "money": "Money",
      "bank_balance": "Bank Balance",
      "joined": "Joined the server",
      "title": "${name}'s profile"
    },
    "errors": {
      "no_bot": "You can't get the profile of a bot"
    }
  },
    """

    name: str
    description: str = ""
    options: dict[str, Option] = {}
    strings: dict[str, str] = {}
    errors: dict[str, str] = {}

    class Config:
        allow_mutation = False

    def get_option(self, name: str):
        return self.options.get(name, f"[{name}]")

    def get_string(self, name: str):
        return TranslatedString(self.strings.get(name, f"[{name}]"))

    def get_error(self, name: str):
        return TranslatedString(self.errors.get(name, f"[{name}]"))

    def __getitem__(self, item):
        return self.get_string(item)



@dataclasses.dataclass
class Opt:
    name: Localized
    description: Localized

@dataclasses.dataclass
class CommandForInit:
    name: Localized
    description: Localized

    options: dict[str, Opt]


class TranslatedString:

    def __init__(self, raw_string: str):
        self.raw_string = raw_string
        self.template = Template(raw_string)

    def apply(self, **kwargs):
        dt = self.template.safe_substitute(**kwargs)
        self.raw_string = dt
        return dt

    def __str__(self):
        return self.raw_string


class TranslatedGroup:
    def __init__(self, raw_group: dict[str, str | dict], group_not_found: bool = False):
        self._raw_group = raw_group
        self.group_not_found = group_not_found

    def get_string(self, string: str):
        if self.group_not_found:
            return f"[{string}][error=group_not_found]"

        raw_string = self._raw_group.get(string, f"[{string}][error=string_not_found]")

        return TranslatedString(raw_string)

    def get_command(self, command: str):
        raw_command: dict = self._raw_group.get(command, None)

        if not raw_command:
            return Command(
                name=command,
                description=f"[{command}][error=command_not_found]",
                options={},
                strings={},
                errors={},
            )

        return Command(
            **raw_command
        )


class TranslatedLanguage:
    def __init__(self, raw_lang: dict[str, dict[str, str]]):
        self._raw_lang = raw_lang

    def get_group(self, group: str):
        group_raw = self._raw_lang.get(group, None)
        if not group_raw:
            return TranslatedGroup({}, group_not_found=True)

        return TranslatedGroup(group_raw)


class TranslationData:
    def __init__(self, raw_translations: dict[str, dict[str, dict[str, str]]]):
        self._raw_translations = raw_translations

    def get_language(self, lang: str):
        raw_lang = self._raw_translations.get(lang, None)
        if not raw_lang:
            raise ValueError(f"Language {lang} not found")

        return TranslatedLanguage(raw_lang)


class TranslationFile(NamedTuple):
    path: str
    group: str
    lang: str


class TranslationsManager:
    """

    Files structure:
    <@dir> / <@group> / <@lang>.json

    Example:
    /translations
        /common
            /en.json
            /ru.json
            /uk.json

    """

    def __init__(self, languages: list[str], dir_path: str | Path):
        self.languages = languages
        self.dir_path = dir_path

        self._translation_files_paths: list[TranslationFile] | None = None

    def load_translation_files_paths(self):
        groups = os.listdir(self.dir_path)

        translation_files_paths = [
            TranslationFile(
                path=os.path.join(str(self.dir_path), group, f"{lang}.json"), group=group, lang=lang
            )
            for group in groups
            for lang in self.languages
        ]

        self._translation_files_paths = translation_files_paths
        return translation_files_paths

    def load_raw_translations(self):
        if not self._translation_files_paths:
            self.load_translation_files_paths()

        translations = {lang: {} for lang in self.languages}

        for file in self._translation_files_paths:
            with open(file.path, "r", encoding="UTF-8") as file_handler:
                file_content: dict[str, str] = json.load(file_handler)

                translations[file.lang][file.group] = file_content

        return translations

    @staticmethod
    def check_translations(translations):
        """
        Check if all translations have the same keys
        Each language has its groups, each group has its keys:strings
        This function checks if the same group has the same keys in all languages
        @param translations:
        @return:
        """

        keys_warned = []

        for lang in translations:
            for group in translations[lang]:
                for lang2 in translations:
                    if lang == lang2:
                        continue
                    if group not in translations[lang2]:
                        print(f"[WARNING] Group {group} not found in {lang2}")
                        continue
                    for key in translations[lang][group]:
                        if key not in translations[lang2][group] and key not in keys_warned:
                            print(
                                f"[WARNING] Key {key} not found in {lang2} [{group=}] but found "
                                f"in {lang} [{group=}]"
                            )
                            keys_warned.append(key)
                            continue

    def process_translations(self) -> TranslationData:
        translations = self.load_raw_translations()
        self.check_translations(translations)
        return TranslationData(translations)
