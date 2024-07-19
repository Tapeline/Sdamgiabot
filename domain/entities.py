import random
from abc import ABC, abstractmethod
from typing import Optional


class AbstractSubject(ABC):
    """ABC for all subjects"""
    @abstractmethod
    def get_uid(self) -> str:
        """Get subject uid"""
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        """Get subject name"""
        raise NotImplementedError

    def __eq__(self, __value):
        if not isinstance(__value, AbstractSubject):
            return False
        return self.get_uid() == __value.get_uid()

    def __ne__(self, __value):
        return not self.__eq__(__value)

    def __repr__(self):
        return f"{self.get_uid()}:{self.get_name()}"


TaskID = str
TaskTypeID = str
IsTaskSolved = bool


class AbstractTaskType(ABC):
    """ABC for task types"""
    @abstractmethod
    def get_name(self) -> str:
        """Get type name"""
        raise NotImplementedError

    @abstractmethod
    def get_uid(self) -> TaskTypeID:
        """Get type unique id"""
        raise NotImplementedError

    def __repr__(self):
        return f"{self.get_uid()}:{self.get_name()}"


class AbstractTask(ABC):
    """ABC for all tasks"""
    @abstractmethod
    def initialize(self, client, as_image, image_path):
        """Fill blank fields"""
        raise NotImplementedError

    @abstractmethod
    def get_uid(self) -> TaskID:
        """Get task unique ID"""
        raise NotImplementedError

    @abstractmethod
    def get_subject(self) -> AbstractSubject:
        """Get corresponding subject"""
        raise NotImplementedError

    @abstractmethod
    def get_type(self) -> AbstractTaskType:
        """Get corresponding type"""
        raise NotImplementedError

    @abstractmethod
    def get_text(self) -> str:
        """Get task text"""
        raise NotImplementedError

    @abstractmethod
    def get_image_urls(self) -> list[str]:
        """Get task image urls"""
        raise NotImplementedError

    @abstractmethod
    def get_task_url(self) -> str:
        """Get task url"""
        raise NotImplementedError

    def __repr__(self):
        return f"Task:{self.get_uid()}"


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
    def get_task(self, subject: AbstractSubject, task_id: TaskID) -> AbstractTask | None:
        """Get task"""
        raise NotImplementedError

    @abstractmethod
    def get_tasks(self, subject: AbstractSubject, task_type: AbstractTaskType) \
            -> list[AbstractTask]:
        """Get list of tasks"""
        raise NotImplementedError

    @abstractmethod
    def get_subjects(self) -> list[AbstractSubject]:
        """Get list of tasks"""
        raise NotImplementedError

    @abstractmethod
    def get_task_types_in_subject(self, subject: AbstractSubject | str) -> list[AbstractTaskType]:
        """Get list of tasks"""
        raise NotImplementedError

    @staticmethod
    def _transform_exclusion_list(exclude_tasks: Optional[list[TaskID | AbstractTask]]) \
            -> list[TaskID]:
        """Transform optional list of tasks or their ids to consistent list of ids"""
        return [x.get_uid() if isinstance(x, AbstractTask) else x
                for x in exclude_tasks]

    def get_tasks_excluding(self,
                            subject: AbstractSubject, task_type: AbstractTaskType,
                            exclude_tasks: Optional[list[TaskID | AbstractTask]] = None) \
            -> list[AbstractTask]:
        """Get list of tasks regarding exclusion list"""
        tasks = self.get_tasks(subject, task_type)
        exclude_tasks = self._transform_exclusion_list(exclude_tasks)
        tasks = filter(lambda x: x not in exclude_tasks, tasks)
        return list(tasks)

    def get_random_task(self,
                        subject: AbstractSubject, task_type: AbstractTaskType,
                        exclude_tasks: Optional[list[TaskID | AbstractTask]] = None) \
            -> AbstractTask | None:
        """
        Get random task of this subject regarding exclusion list.
        If no tasks found, None is returned
        """
        tasks = self.get_tasks_excluding(subject, task_type, exclude_tasks)
        if len(tasks) == 0:
            return None
        return random.choice(tasks)

    @abstractmethod
    def submit_solution(self, task: TaskID | AbstractTask, solution: str) -> IsTaskSolved:
        """Submit solution and say whether you were right or wrong"""
        raise NotImplementedError


UserId = int


class AbstractUserRepository(ABC):
    @abstractmethod
    def get_user_preferred_topics(self, user_id: UserId) \
            -> list[tuple[str, TaskTypeID]]:
        """Get preferred topics for user"""
        raise NotImplementedError

    @abstractmethod
    def set_user_preferred_topics(self,
                                  user_id: UserId,
                                  topics: list[tuple[str, TaskTypeID]]) -> None:
        """Set preferred topics for user"""
        raise NotImplementedError

    @abstractmethod
    def mark_task_seen(self, user_id: UserId, subject: str, task: TaskID) \
            -> list[tuple[AbstractSubject, AbstractTaskType]]:
        """Do not recommend this task anymore"""
        raise NotImplementedError

    @abstractmethod
    def has_seen_task(self, user_id: UserId, task: AbstractTask) -> bool:
        """Recommend this task or not"""
        raise NotImplementedError

    @abstractmethod
    def get_seen_tasks(self, user_id: UserId) -> list[tuple]:
        """Get list of seen tasks in format of list[tuple[subject_id, task_id]]"""
        raise NotImplementedError

    @abstractmethod
    def get_user_ids_for_daily_task(self) -> list[UserId]:
        """Get list of all registered users"""
        raise NotImplementedError

    @abstractmethod
    def switch_receive_daily_task_for_user(self, user_id: UserId) -> bool:
        """Switch subscription. Return newest state"""
        raise NotImplementedError
