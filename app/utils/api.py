import time

from starlette.requests import Request

from app import Bot


def wait_till_ready(bot: Bot):
    if not bot.is_ready():
        time.sleep(.1)
        if not bot.is_ready():
            return wait_till_ready(bot)

    return bot


def get_bot_from_request(request: Request) -> Bot:
    bot: Bot = request.app.state.bot

    bot = wait_till_ready(bot)

    return bot
