import os
import uuid

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReactionTypeEmoji
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from sdamgiabot.application.interactors import (
    CheckAnswerInteractor,
    GenerateTaskInteractor,
)
from sdamgiabot.domain.entities import (
    AbstractTaskRepository,
    AbstractUserRepository, PreferredTopic,
)
from sdamgiabot.infrastructure.taskrepository.client import GIAClient
from sdamgiabot.presentation.sender import send_task

router = Router()


class GlobalStates(StatesGroup):
    MAIN = State()
    ANSWERING = State()


answer_user_data: dict[int, str] = {}


@router.callback_query(F.data.startswith("answer_"))
async def cmd_send_answer(
        callback_query: CallbackQuery,
        state: FSMContext
) -> None:
    await state.set_state(GlobalStates.ANSWERING)
    await callback_query.answer("Введите ответ в сообщении")
    answer_user_data[
        callback_query.from_user.id
    ] = callback_query.data.removeprefix("answer_")


@router.message(GlobalStates.ANSWERING)
@inject
async def cmd_check_answer(
        message: Message,
        state: FSMContext,
        interactor: FromDishka[CheckAnswerInteractor]
) -> None:
    subject_name, task_id = answer_user_data[message.from_user.id].split(":")
    is_correct = await interactor(subject_name, task_id, message.text)
    if not is_correct:
        await message.react([ReactionTypeEmoji(emoji="👎")])
    else:
        await message.react([ReactionTypeEmoji(emoji="👍")])
        await state.set_state(GlobalStates.MAIN)
        answer_user_data.pop(message.from_user.id)


@router.message(Command("gen"))
@inject
async def cmd_gen_task(
        message: Message,
        state: FSMContext,
        interactor: FromDishka[GenerateTaskInteractor],
        client: FromDishka[GIAClient]
) -> None:
    task = await interactor(message.from_user.id)
    if not task:
        await message.answer("Не удалось найти задачу")
        return
    img_path = f"{uuid.uuid4()}.png"
    client.get_problem_as_image(task.subject.uid, task.uid, img_path)
    await send_task(message.bot, message.from_user.id, img_path, task)
    os.remove(img_path)


@router.message(Command("gettopics"))
@inject
async def cmd_get_topics(
        message: Message,
        command: CommandObject,
        user_repo: FromDishka[AbstractUserRepository]
):
    topics = user_repo.get_user_preferred_topics(message.from_user.id)
    topics_str = ";".join(map(lambda x: ":".join(x), topics))
    await message.answer(
        "<b>Выбранные темы:</b>\n"
        "<i>Формат: </i>\n<code>код_предмета:№_задания;"
        "код_предмета2:№_задания2...</code>\n\n"
        f"<code>{topics_str}</code>"
    )


@router.message(Command("settopics"))
@inject
async def cmd_set_topics(
        message: Message,
        command: CommandObject,
        user_repo: FromDishka[AbstractUserRepository]
):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    topics = [
        PreferredTopic(*x.split(":", maxsplit=1))
        for x in command.args.split(";")
    ]
    user_repo.set_user_preferred_topics(message.from_user.id, topics)
    await message.answer(
        f"<b>Темы обновлены: </b><code>{command.args}</code>"
    )


@router.message(Command("sub"))
@inject
async def cmd_subscribe_unsubscribe(
        message: Message,
        command: CommandObject,
        user_repo: FromDishka[AbstractUserRepository]
):
    current = user_repo.switch_receive_daily_task_for_user(
        message.from_user.id
    )
    if current:
        await message.answer(
            "<b>✅ Теперь вы подписаны на ежедневные задания</b>"
        )
    else:
        await message.answer(
            "<b>❌ Подписка на ежедневные задания отменена</b>"
        )


@router.message(Command("help"))
@inject
async def cmd_help(
        message: Message,
        command: CommandObject,
        task_repo: FromDishka[AbstractTaskRepository]
):
    await message.answer(
        "<b>❔ Помощь</b>\n\n"
        "<code>/help</code> - это меню\n\n"
        "<code>/gen</code> - сгенерировать задачу\n\n"
        "<code>/settopics темы</code> - задать интересующие темы в формате:\n"
        "<code>код_предмета:номер_задания</code>. "
        "Если нужно несколько - разделить <code>;</code>. Пример: "
        "<code>inf:1;inf:2;rus:5</code>\n"
        "Доступные коды предметов: \n" +
        ", \n".join(f"<code>{x.uid}</code> - {x.name}"
                  for x in task_repo.get_subjects()) +
        "\n\n"
        "<code>/gettopics</code> - получить заданные интересующие темы\n\n"
        "<code>/sub</code> - вкл./выкл. ежедневную рассылку заданий\n\n"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    await message.answer(
        "Добро пожаловать.\n"
        "<code>/help</code> для просмотра команд"
    )
