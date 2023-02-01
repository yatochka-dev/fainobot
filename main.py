import asyncio
import os

from disnake import CommandInter
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


@bot.slash_command(
    name="super"
)
async def super_cmd(inter: CommandInter):
    await inter.send("Gay")


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
    bot.logger.debug("Loading environment variables")
    load_env()
    bot.logger.debug("Loading cogs")
    await load_cogs()
    bot.logger.debug("Connecting to database")

    await prisma.connect(timeout=30)

    discord_token = os.getenv("DISCORD_TOKEN")

    # Print message with each logger level

    bot.logger.info(f"Starting bot in {os.getenv('STATE_NAME').title()} mode.")

    if isinstance(discord_token, str) and len(discord_token) > 5:
        asyncio.create_task(bot.start(discord_token))
    else:
        bot.logger.critical("No Discord token found!")




@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()
