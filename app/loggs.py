import logging
import sys

from colorama import Fore, Style, Back

__all__ = ["logger", "disnake_logger"]

FORMATS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.BLUE,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Back.RED + Fore.WHITE,
}

red_stick = Fore.LIGHTRED_EX + " | " + Style.RESET_ALL
red_column = Fore.LIGHTRED_EX + ":" + Style.RESET_ALL
red_dash = Fore.LIGHTRED_EX + " - " + Style.RESET_ALL

FORMAT = (
    Fore.GREEN
    + u"%(asctime)s "
    + Style.RESET_ALL
    + red_stick
    + u"{primary_color}\033[1m%(levelname)s\033[0m{spaces}"
    + red_stick
    + Fore.CYAN
    + u"%(filename)s"
    + red_column
    + Fore.CYAN
    + u"%(name)s"
    + red_column
    + Fore.CYAN
    + u"%(lineno)d"
    + red_dash
    + u"{secondary_color}%(message)s"
    + Style.RESET_ALL
)


def get_format_spaces(record: int):
    levelToSpaces = {
        logging.CRITICAL: 2,
        logging.ERROR: 5,
        logging.WARNING: 3,
        logging.INFO: 6,
        logging.DEBUG: 5,
        logging.NOTSET: 4,
    }

    return levelToSpaces[record]


def get_format(record: int):
    spaces = " " * get_format_spaces(record)
    color = FORMATS[record]
    return u"{}".format(FORMAT.format(spaces=Style.RESET_ALL + spaces,primary_color=color,secondary_color=color,))


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def format(self, record):
        log_fmt = get_format(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)

disnake_logger = logging.getLogger("disnake")
disnake_logger.setLevel(logging.WARNING)
disnake_logger.addHandler(handler)
