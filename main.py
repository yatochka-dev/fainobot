# -*- coding: utf-8 -*-
import asyncio
import os
import sys


from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app import Bot
from app.apis import apis
from app.db import prisma

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(apis, prefix="/api")

bot = Bot()

app.state.bot = bot


def load_env():
    environments = {
        "dev": ".env.development",
        "prod": ".env.production",
    }

    current_state = "dev" if bot.APP_SETTINGS.TESTING else "prod"

    load_dotenv(dotenv_path=bot.BASE_DIR / environments[current_state])


async def load_cogs():
    cogs_folder = bot.BASE_DIR / "app" / "cogs"
    for cog in cogs_folder.glob("*.py"):
        bot.logger.debug("Found cog: {}".format(cog.stem))
        if cog.name.startswith("_"):
            bot.logger.debug("Skipping cog: {}".format(cog.stem))
            continue
        bot.load_extension(f"app.cogs.{cog.stem}")
        bot.logger.info("Loaded cog: {}".format(cog.stem))


@app.on_event("startup")
async def startup():
    import locale

    if locale.getpreferredencoding().upper() != "UTF-8":
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    bot.logger.debug("Loading environment variables")
    load_env()
    bot.logger.debug("Loaded environment variables")

    bot.logger.debug("Loading cogs")
    await load_cogs()
    bot.logger.debug("Loaded cogs")

    bot.logger.debug("Connecting to database")
    await prisma.connect()
    bot.logger.debug("Connected to database")

    discord_token = os.getenv("DISCORD_TOKEN")

    # Print message with each logger level
    state_name = os.getenv("STATE_NAME") or "Production"
    bot.logger.info(f"Starting bot in {state_name.title()} mode.")

    if isinstance(discord_token, str) and len(discord_token) > 0:
        asyncio.create_task(bot.start(discord_token))
    else:
        bot.logger.critical("No Discord token found!")


@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()
