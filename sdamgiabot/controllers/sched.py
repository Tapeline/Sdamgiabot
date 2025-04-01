import uuid

from aiogram import Bot
from dishka import FromDishka

from sdamgiabot.application.interactors import GenerateTaskInteractor
from sdamgiabot.domain.entities import AbstractUserRepository
from sdamgiabot.infrastructure.scheduling import inject
from sdamgiabot.infrastructure.taskrepository.client import GIAClient
from sdamgiabot.controllers.sender import send_task


@inject
async def daily_task_gen(
        user_repo: FromDishka[AbstractUserRepository],
        client: FromDishka[GIAClient],
        bot: FromDishka[Bot],
        interactor: FromDishka[GenerateTaskInteractor]
) -> None:
    """Generate daily task for all users."""
    for user_id in user_repo.get_user_ids_for_daily_task():
        task = await interactor(user_id)
        if task is None:
            await bot.send_message(
                user_id, "Не удалось сгенерировать ежедневное задание."
            )
        img_path = f"{uuid.uuid4()}.png"
        client.get_problem_as_image(task.subject.uid, task.uid, img_path)
        await send_task(bot, user_id, img_path, task, is_daily=True)
