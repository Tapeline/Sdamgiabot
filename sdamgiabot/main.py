import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from sdamgiabot.config import Config
from sdamgiabot import constants
from sdamgiabot.controllers.bot import router as main_router
from sdamgiabot.controllers.sched import daily_task_gen
from sdamgiabot.di import AppProvider
from sdamgiabot.infrastructure import scheduling
from sdamgiabot.infrastructure.persistence import models
from sdamgiabot.infrastructure.scheduling import run_periodic

config = Config()
bot = Bot(
    token=config.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
container = make_async_container(
    AppProvider(),
    context={
        Config: config,
        Bot: bot
    }
)


async def main() -> None:
    dispatcher = Dispatcher()
    dispatcher.include_router(main_router)
    scheduling.setup_dishka(container)
    setup_dishka(container, dispatcher)
    run_periodic(constants.DAY, daily_task_gen)  # type: ignore
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    models.init()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
