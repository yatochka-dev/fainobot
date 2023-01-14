import re
from typing import NamedTuple


def convert_text_to_bold(string: str, /) -> str:
    return "\033[1m" + string + "\033[0m"


def get_mentions_as_list(text: str) -> list[str]:
    return re.findall(r"<@!\d+>|<@&\d+>|<#\d+>|<@\d+>|@everyone|@here", text)


def get_mentions_as_string(text: str, /) -> str:
    mentions = get_mentions_as_list(text)
    return " ".join(mentions)


class MMLength(NamedTuple):
    min: int
    max: int

    def __str__(self):
        return f"{self.min}-{self.max}"

    def __contains__(self, item: str) -> bool:
        """str in MMLength"""

        if not isinstance(item, str):
            return False

        return self.min <= len(item) <= self.max

    def validate_many(self, *items: str) -> bool:
        """Validate multiple items"""

        return all(item in self for item in items)
