from aiogram import Bot
from dishka import (
    Provider,
    Scope,
    from_context,
    provide,
    provide_all,
)

from sdamgiabot.application.interactors import (
    CheckAnswerInteractor,
    GenerateTaskInteractor,
)
from sdamgiabot.config import Config
from sdamgiabot.domain.entities import (
    AbstractTaskRepository,
    AbstractUserRepository,
)
from sdamgiabot.infrastructure.persistence.repo import UserRepository
from sdamgiabot.infrastructure.taskrepository.client import GIAClient
from sdamgiabot.infrastructure.taskrepository.repo import TaskRepository


class AppProvider(Provider):
    config = from_context(Config, scope=Scope.APP)

    bot = from_context(Bot, scope=Scope.APP)

    task_repo = provide(
        TaskRepository,
        scope=Scope.APP,
        provides=AbstractTaskRepository
    )
    user_repo = provide(
        UserRepository,
        scope=Scope.APP,
        provides=AbstractUserRepository
    )
    client = provide(GIAClient, scope=Scope.APP)

    interactors = provide_all(
        CheckAnswerInteractor,
        GenerateTaskInteractor,
        scope=Scope.APP
    )
