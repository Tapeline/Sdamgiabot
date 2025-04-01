import random
import uuid

from dishka import FromDishka

from sdamgiabot.domain.entities import (
    AbstractTask,
    AbstractTaskRepository,
    AbstractUserRepository,
    UserId,
)


class GenerateTaskInteractor:
    def __init__(
            self,
            user_repo: FromDishka[AbstractUserRepository],
            task_repo: FromDishka[AbstractTaskRepository]
    ) -> None:
        self.user_repo = user_repo
        self.task_repo = task_repo

    async def __call__(self, user_id: UserId) -> AbstractTask | None:
        preferred_topics = self.user_repo.get_user_preferred_topics(user_id)
        if not preferred_topics:
            return None
        random_topic = random.choice(preferred_topics)
        seen_tasks = self.user_repo.get_seen_tasks(user_id)
        subject = self.task_repo.get_subject(random_topic.subject)
        task_types = self.task_repo.get_task_types_in_subject(subject)
        if len(task_types) < int(random_topic.type):
            return None
        task_type = task_types[int(random_topic.type) - 1]
        exclude = [x[1] for x in seen_tasks if x[0] == subject.uid]
        task = self.task_repo.get_random_task(subject, task_type, exclude)
        if task is None:
            return None
        task.initialize(
            self.task_repo.get_client(),
            as_image=True,
            image_path=f"image_{uuid.uuid4()}.png"
        )
        self.user_repo.mark_task_seen(user_id, subject.uid, task.uid)
        return task


class CheckAnswerInteractor:
    def __init__(self, task_repo: FromDishka[AbstractTaskRepository]) -> None:
        self.task_repo = task_repo

    async def __call__(
            self,
            subject_id: str,
            task_id: str,
            answer: str
    ) -> bool:
        subj = self.task_repo.get_subject(subject_id)
        task = self.task_repo.get_task(subj, task_id)
        return self.task_repo.submit_solution(task, answer.lower())
