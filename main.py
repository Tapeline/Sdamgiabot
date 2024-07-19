# pylint: disable=missing-function-docstring
# pylint: disable=unused-argument

import asyncio
import logging
import os
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (Message, FSInputFile, InlineKeyboardMarkup,
                           InlineKeyboardButton, ReactionTypeEmoji)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import sched
from domain.action import generate_task_for_user, ImageMessage, check_answer_for_task
from storage import models
from storage.repo import UserRepository
from taskrepository.repo import TaskRepository

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
user_repo = UserRepository()
task_repo = TaskRepository()
scheduler = AsyncIOScheduler(timezone="Etc/GMT+5")
scheduler.add_job(
    sched.daily_generation,
    trigger="interval",
    seconds=60*60*24,
    kwargs={
        "bot": bot,
        "task_repo": task_repo,
        "user_repo": user_repo
    }
)


@dp.message(Command("gettopics"))
async def cmd_get_topics(message: Message, command: CommandObject):
    topics = user_repo.get_user_preferred_topics(message.from_user.id)
    topics_str = ";".join(map(lambda x: ":".join(x), topics))
    await message.answer(
        "<b>Выбранные темы:</b>\n"
        "<i>Формат: </i>\n<code>код_предмета:№_задания;код_предмета2:№_задания2...</code>\n\n"
        f"<code>{topics_str}</code>"
    )


@dp.message(Command("settopics"))
async def cmd_set_topics(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    topics = [tuple(x.split(":", maxsplit=1)) for x in command.args.split(";")]
    user_repo.set_user_preferred_topics(message.from_user.id, topics)
    await message.answer(f"<b>Темы обновлены: </b><code>{command.args}</code>")


@dp.message(Command("gen"))
async def cmd_generate_task(message: Message, command: CommandObject):
    await message.react([ReactionTypeEmoji(emoji="👍")])
    response = generate_task_for_user(
        message.from_user.id,
        user_repo, task_repo,
        as_image=True
    )

    if response is None:
        await message.answer("Не удалось сгенерировать. Выберите темы")

    if isinstance(response, ImageMessage):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Открыть на сайте", url=response.url),
        ]])
        await message.answer_photo(
            FSInputFile(response.image),
            caption=response.text,
            reply_markup=keyboard
        )
        os.remove(response.image)
    else:
        await message.answer(response.text)


@dp.message(Command("ans"))
async def cmd_answer(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы (2)")
        return
    args = command.args.split()
    if len(args) != 2:
        await message.answer("Ошибка: не переданы аргументы (2)")
        return
    ids, ans = args
    subject, task = ids.split(":")
    is_correct = check_answer_for_task(task_repo, subject, task, ans)
    if is_correct:
        await message.answer("<b>✅ Верно</b>")
    else:
        await message.answer("<b>❌ Неверно</b>")


@dp.message(Command("sub"))
async def cmd_subscribe_unsubscribe(message: Message, command: CommandObject):
    current = user_repo.switch_receive_daily_task_for_user(message.from_user.id)
    if current:
        await message.answer("<b>✅ Теперь вы подписаны на ежедневные задания</b>")
    else:
        await message.answer("<b>❌ Подписка на ежедневные задания отменена</b>")


@dp.message(Command("help"))
async def cmd_help(message: Message, command: CommandObject):
    await message.answer(
        "<b>❔ Помощь</b>\n\n"
        "<code>/help</code> - это меню\n\n"
        "<code>/gen</code> - сгенерировать задачу\n\n"
        "<code>/settopics темы</code> - задать интересующие темы в формате:\n"
        "<code>код_предмета:номер_задания</code>. "
        "Если нужно несколько - разделить <code>;</code>. Пример: "
        "<code>inf:1;inf:2;rus:5</code>\n"
        "Доступные коды предметов: \n" +
        ", \n".join(f"<code>{x.get_uid()}</code> - {x.get_name()}"
                  for x in task_repo.get_subjects()) +
        "\n\n"
        "<code>/gettopics</code> - получить заданные интересующие темы\n\n"
        "<code>/ans идентификатор_задания ответ</code> - проверить ответ на задание."
        "Шаблон для этой команды выводится с каждым заданием\n\n"
        "<code>/sub</code> - вкл./выкл. ежедневную рассылку заданий\n\n"
    )


@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    await message.answer(
        "Добро пожаловать.\n"
        "<code>/help</code> для просмотра команд"
    )


async def main() -> None:
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    models.init()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
