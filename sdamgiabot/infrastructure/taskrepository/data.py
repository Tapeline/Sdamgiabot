from sdamgiabot.domain.entities import (
    AbstractTask, AbstractSubject, TaskID,
    AbstractTaskType, TaskTypeID,
)
from .client import GIAClient


class Task(AbstractTask):
    """Task impl"""

    def __init__(
            self, uid: TaskID,
            subject: AbstractSubject,
            task_type: AbstractTaskType,
            task_url: str = "",
            answer: str | None = None
    ):
        self._answer = answer
        self._uid = uid
        self.is_initialized = False
        self._subject = subject
        self._task_url = task_url
        self._task_type = task_type
        self.image_path: None | str = None

    def initialize(
            self,
            client: GIAClient,
            as_image=False,
            image_path: str | None = None
    ):
        if as_image and image_path is not None:
            client.get_problem_as_image(
                self._subject.uid, self._uid, image_path
            )
            self.image_path = image_path
            self._task_url = client.get_problem_url(
                self._subject.uid, self._uid
            )
            return
        task = client.get_problem_by_id(self._subject.uid, self._uid)
        self._task_url = task["url"]
        self._answer = task["answer"]
        self.is_initialized = True

    @property
    def uid(self) -> TaskID:
        return self._uid

    @property
    def subject(self) -> AbstractSubject:
        return self._subject

    @property
    def task_url(self) -> str:
        return self._task_url

    @property
    def type(self) -> AbstractTaskType:
        return self._task_type

    @property
    def answer(self) -> str | None:
        return self._answer


class Subject(AbstractSubject):
    """Subject impl"""

    def __init__(self, uid: str, name: str):
        self._uid = uid
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def uid(self) -> str:
        return self._uid


class TaskType(AbstractTaskType):
    """Task type impl"""

    def __init__(self, uid: TaskTypeID, name: str, categories: list[str]):
        self._uid = uid
        self._name = name
        self.categories = categories

    @property
    def name(self) -> str:
        return self._name

    @property
    def uid(self) -> TaskTypeID:
        return self._uid
