"""
User repo impl
"""

from domain.entities import (AbstractUserRepository, UserId,
                             AbstractTask, TaskID, TaskTypeID)
from storage.models import User


class UserRepository(AbstractUserRepository):
    """User repo impl"""
    # pylint: disable=missing-function-docstring
    def _ensure_user_exists(self, user_id: UserId):
        """If user does not exist -> create"""
        if not User.select().where(User.tg_id == user_id).exists():
            user = User(tg_id=user_id, topics="", already_seen="")
            user.save()

    def get_user_preferred_topics(self, user_id: UserId) -> list[tuple[str, TaskTypeID]]:
        self._ensure_user_exists(user_id)
        topics_str = User.get(User.tg_id == user_id).topics
        return [(x[:x.find(":")], x[x.find(":")+1:]) for x in topics_str.split(";")]

    def set_user_preferred_topics(self, user_id: UserId, topics: list[tuple[str, TaskTypeID]]) -> None:
        self._ensure_user_exists(user_id)
        topics_str = ";".join(map(lambda x: f"{x[0]}:{x[1]}", topics))
        user = User.get(User.tg_id == user_id)
        user.topics = topics_str
        user.save()

    def set_raw_user_preferred_topics(self, user_id: UserId, topics: str) -> None:
        self._ensure_user_exists(user_id)
        user = User.get(User.tg_id == user_id)
        user.topics = topics
        user.save()

    def mark_task_seen(self, user_id: UserId, subject: str, task: TaskID) -> None:
        self._ensure_user_exists(user_id)
        seen_str = User.get(User.tg_id == user_id).already_seen
        seen = seen_str.split(";")
        seen.append(f"{subject}:{task}")
        seen_str = ";".join(seen)
        user = User.get(User.tg_id == user_id)
        user.already_seen = seen_str
        user.save()

    def get_seen_tasks(self, user_id: UserId) -> list[tuple]:
        self._ensure_user_exists(user_id)
        seen_str = User.get(User.tg_id == user_id).already_seen
        return [(x[:x.find(":")], x[x.find(":")+1:]) for x in seen_str.split(";")]

    def has_seen_task(self, user_id: UserId, task: AbstractTask) -> bool:
        self._ensure_user_exists(user_id)
        seen_str = User.get(User.tg_id == user_id).already_seen
        seen = seen_str.split(";")
        return f"{task.get_subject().get_uid()}:{task.get_uid()}" in seen

    def get_user_ids_for_daily_task(self) -> list[UserId]:
        return [user.tg_id for user in User.select().where(User.receive_daily == True)]

    def switch_receive_daily_task_for_user(self, user_id: UserId) -> bool:
        self._ensure_user_exists(user_id)
        user = User.get(User.tg_id == user_id)
        user.receive_daily = not user.receive_daily
        user.save()
        return user.receive_daily
