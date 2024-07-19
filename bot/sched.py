"""
Provides scheduled function
"""

import os

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from domain.action import generate_task_for_user, ImageMessage
from domain.entities import AbstractUserRepository, AbstractTaskRepository


async def daily_generation(user_repo: AbstractUserRepository,
                           task_repo: AbstractTaskRepository,
                           bot: Bot):
    """Generate daily task for all users"""
    for user_id in user_repo.get_user_ids_for_daily_task():
        response = generate_task_for_user(user_id, user_repo, task_repo, as_image=True)

        if response is None:
            await bot.send_message(user_id, "Не удалось сгенерировать ежедневное задание.")

        if isinstance(response, ImageMessage):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Открыть на сайте", url=response.url),
            ]])
            await bot.send_photo(
                user_id,
                FSInputFile(response.image),
                caption=f"<i>📅 Ежедневное задание</i>\n{response.text}",
                reply_markup=keyboard
            )
            os.remove(response.image)
        else:
            await bot.send_message(user_id, f"<i>📅 Ежедневное задание</i>\n{response.text}")
