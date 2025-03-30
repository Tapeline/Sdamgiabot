from aiogram import Bot
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from sdamgiabot.domain.entities import AbstractTask


async def send_task(
        bot: Bot | None,
        user_id: int,
        image_path: str,
        task: AbstractTask
) -> None:
    if not bot:
        raise AssertionError("Bot not set")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть на сайте",
                    url=task.task_url
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Ответить",
                    callback_data=f"answer_{task.subject.uid}:{task.uid}"
                )
            ]
        ]
    )
    await bot.send_photo(
        user_id,
        FSInputFile(image_path),
        caption=(
            f"<i>📅 Ежедневное задание</i>\n"
            f"{task.subject.name} / Тип {task.type.name}"
        ),
        reply_markup=keyboard
    )
