from typing import NamedTuple


class MMNumber(NamedTuple):
    min: int
    max: int

    def __contains__(self, item: int):
        if not isinstance(item, int):
            return False

        return self.min <= item <= self.max
