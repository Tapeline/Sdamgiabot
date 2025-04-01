import random
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Optional

from attr import frozen


class AbstractSubject(ABC):
    """ABC for all subjects."""

    @property
    @abstractmethod
    def uid(self) -> str:
        """Get subject uid."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get subject name."""

    def __eq__(self, __value):
        if not isinstance(__value, AbstractSubject):
            return False
        return self.uid == __value.uid

    def __ne__(self, __value):
        return not self.__eq__(__value)

    def __repr__(self):
        return f"{self.uid}:{self.name}"


type TaskID = str
type TaskTypeID = str
type IsTaskSolved = bool


class AbstractTaskType(ABC):
    """ABC for task types."""

    @property
    @abstractmethod
    def uid(self) -> str:
        """Get type uid."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get type name."""

    def __repr__(self):
        return f"{self.uid}{self.name}"


class AbstractTask(ABC):
    """ABC for all tasks."""

    @abstractmethod
    def initialize(self, client, as_image, image_path):
        """Fill blank fields."""

    @property
    @abstractmethod
    def uid(self) -> TaskID:
        """Get task unique ID."""

    @property
    @abstractmethod
    def subject(self) -> AbstractSubject:
        """Get corresponding subject."""

    @property
    @abstractmethod
    def type(self) -> AbstractTaskType:
        """Get corresponding type."""

    @property
    @abstractmethod
    def task_url(self) -> str:
        """Get task url."""

    def __repr__(self):
        return f"Task:{self.uid}"


class AbstractTaskRepository(ABC):
    """ABC for task repositories"""

    @abstractmethod
    def get_client(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_subject(subj_id: str) -> AbstractSubject | None:
        raise NotImplementedError

    @abstractmethod
    def get_task(
            self,
            subject: AbstractSubject,
            task_id: TaskID
    ) -> AbstractTask | None:
        """Get task"""

    @abstractmethod
    def get_tasks(
            self,
            subject: AbstractSubject,
            task_type: AbstractTaskType
    ) -> Sequence[AbstractTask]:
        """Get list of tasks"""

    @abstractmethod
    def get_subjects(self) -> Sequence[AbstractSubject]:
        """Get list of tasks"""

    @abstractmethod
    def get_task_types_in_subject(
            self, subject: AbstractSubject
    ) -> Sequence[AbstractTaskType]:
        """Get list of tasks"""

    @staticmethod
    def _transform_exclusion_list(
            exclude_tasks: Optional[Sequence[TaskID | AbstractTask]]
    ) -> list[TaskID]:
        """Transform list of tasks or their ids to consistent list of ids"""
        return [
            x.uid if isinstance(x, AbstractTask) else x
            for x in exclude_tasks
        ] if exclude_tasks else []

    def get_tasks_excluding(
            self,
            subject: AbstractSubject, task_type: AbstractTaskType,
            exclude_tasks: Optional[Sequence[TaskID | AbstractTask]] = None
    ) -> list[AbstractTask]:
        """Get list of tasks regarding exclusion list"""
        tasks = self.get_tasks(subject, task_type)
        exclude_tasks = self._transform_exclusion_list(exclude_tasks)
        tasks = filter(lambda x: x.uid not in exclude_tasks, tasks)
        return list(tasks)

    def get_random_task(
            self,
            subject: AbstractSubject, task_type: AbstractTaskType,
            exclude_tasks: Optional[Sequence[TaskID | AbstractTask]] = None
    ) -> AbstractTask | None:
        """
        Get random task of this subject regarding exclusion list.
        If no tasks found, None is returned
        """
        tasks = self.get_tasks_excluding(subject, task_type, exclude_tasks)
        if len(tasks) == 0:
            return None
        return random.choice(tasks)

    @abstractmethod
    def submit_solution(
            self,
            task: AbstractTask,
            solution: str
    ) -> IsTaskSolved:
        """Submit solution and say whether you were right or wrong"""
        raise NotImplementedError


type UserId = int


@frozen
class PreferredTopic:
    subject: str
    type: TaskTypeID

    def __str__(self) -> str:
        return f"{self.subject}:{self.type}"


class AbstractUserRepository(ABC):
    @abstractmethod
    def get_user_preferred_topics(
            self, user_id: UserId
    ) -> list[PreferredTopic]:
        """Get preferred topics for user"""

    @abstractmethod
    def set_user_preferred_topics(
            self,
            user_id: UserId,
            topics: list[PreferredTopic]
    ) -> None:
        """Set preferred topics for user"""

    @abstractmethod
    def mark_task_seen(
            self, user_id: UserId, subject: str, task: TaskID
    ) -> list[tuple[AbstractSubject, AbstractTaskType]]:
        """Do not recommend this task anymore"""

    @abstractmethod
    def has_seen_task(self, user_id: UserId, task: AbstractTask) -> bool:
        """Recommend this task or not"""

    @abstractmethod
    def get_seen_tasks(self, user_id: UserId) -> list[tuple[str, TaskID]]:
        """Get list of seen tasks"""

    @abstractmethod
    def get_user_ids_for_daily_task(self) -> list[UserId]:
        """Get list of all registered users"""

    @abstractmethod
    def switch_receive_daily_task_for_user(self, user_id: UserId) -> bool:
        """Switch subscription. Return newest state"""
