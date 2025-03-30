from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from sdamgiabot.controllers import controllers


class AppBot(Bot):
    """Main bot class."""

    def __init__(self, token: str):
        super().__init__(
            token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.storage = MemoryStorage()
        self.dispatcher = Dispatcher(storage=self.storage)
        self.router = Router()
        self.dispatcher.include_router(controllers.router)

    async def run(self):
        """Starts the bot."""
        await self.dispatcher.start_polling(self)
