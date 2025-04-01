"""
Task repo impl
"""
from collections.abc import Sequence

from dishka import FromDishka

from sdamgiabot.domain.entities import (
    AbstractSubject, AbstractTask, AbstractTaskRepository,
    AbstractTaskType, TaskID,
    IsTaskSolved,
)
from .client import GIAClient
from .data import Subject, Task, TaskType

_SUBJECTS_AND_NAMES = {
    'math': 'Математика (проф)',
    'mathb': 'Математика (база)',
    'phys': 'Физика',
    'inf': 'Информатика',
    'rus': 'Русский язык',
    'bio': 'Биология',
    'en': 'Английский язык',
    'chem': 'Химия',
    'geo': 'География',
    'soc': 'Обществознание',
    'de': 'Немецкий язык',
    'fr': 'Французский язык',
    'lit': 'Литература',
    'sp': 'Испанский язык',
    'hist': 'История'
}
_SUBJECTS = [
    Subject(key, value)
    for key, value in _SUBJECTS_AND_NAMES.items()
]


class TaskRepository(AbstractTaskRepository):
    """Repository impl"""

    def __init__(self, client: FromDishka[GIAClient]):
        self.client = client

    def get_client(self):
        return self.client

    @staticmethod
    def get_subject(subj_id: str) -> Subject | None:
        for subj in _SUBJECTS:
            if subj.uid == subj_id:
                return subj
        return None

    def get_tasks(
            self,
            subject: AbstractSubject,
            task_type: TaskType  # type: ignore
    ) -> Sequence[Task]:
        task_ids = []
        for cat in task_type.categories:
            task_ids.extend(
                self.client.get_category_by_id_all(subject.uid, cat)
            )
        return [
            Task(task_id, subject, task_type)
            for task_id in task_ids
        ]

    def get_subjects(self) -> Sequence[Subject]:
        return _SUBJECTS

    def get_task_types_in_subject(
            self, subject: AbstractSubject
    ) -> Sequence[TaskType]:
        topics = self.client.get_catalog(subject.uid)
        return [
            TaskType(
                topic["topic_id"],
                topic["topic_name"],
                [cat["category_id"] for cat in topic["categories"]]
            )
            for topic in topics
        ]

    def submit_solution(
            self,
            task: Task,  # type: ignore
            solution: str
    ) -> IsTaskSolved:
        if task.answer is None:
            return False
        solution = solution.strip().replace(" ", "")
        answer_variants: list[str] = [task.answer]
        if task.subject.uid in {"rus", "en", "de", "fr", "sp"}:
            answer_variants = task.answer.split("|")
        return solution in answer_variants

    def get_task(
            self,
            subject: AbstractSubject,
            task_id: TaskID
    ) -> Task | None:
        response = self.client.get_problem_by_id(subject.uid, task_id)
        return Task(
            response["id"],
            subject,
            response["topic"],
            response["url"],
            response["answer"]
        )
