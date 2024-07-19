from domain.entities import AbstractTaskRepository, TaskID, AbstractTask, IsTaskSolved, AbstractSubject, \
    AbstractTaskType
from taskrepository.client import GIAClient
from taskrepository.data import Subject, Task, TaskType

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
_SUBJECTS = [Subject(key, value) for key, value in _SUBJECTS_AND_NAMES.items()]


class TaskRepository(AbstractTaskRepository):
    """Repository impl"""
    def __init__(self):
        self.client = GIAClient()

    def get_client(self):
        return self.client

    @staticmethod
    def get_subject(subj_id: str) -> Subject | None:
        for subj in _SUBJECTS:
            if subj.get_uid() == subj_id:
                return subj
        return None

    def get_tasks(self, subject: Subject, task_type: TaskType) -> list[Task]:
        task_ids = []
        for cat in task_type.categories:
            task_ids.extend(self.client.get_category_by_id_all(subject.get_uid(), cat))
        return [
            Task(task_id, subject, task_type)
            for task_id in task_ids
        ]

    def get_subjects(self) -> list[Subject]:
        return _SUBJECTS

    def get_task_types_in_subject(self, subject: Subject | str) -> list[TaskType]:
        topics = self.client.get_catalog(subject.get_uid())
        return [
            TaskType(
                topic["topic_id"],
                topic["topic_name"],
                [cat["category_id"] for cat in topic["categories"]]
            )
            for topic in topics
        ]

    def submit_solution(self, task: TaskID | Task, solution: str) -> IsTaskSolved:
        solution = solution.strip().replace(" ", "")
        raw_answer = task.get_answer()
        answer_variants = [raw_answer]
        if task.get_subject().get_uid() in {"rus", "en", "de", "fr", "sp"}:
            answer_variants = raw_answer.split("|")
        return solution in answer_variants

    def get_task(self, subject: Subject, task_id: TaskID) -> Task | None:
        response = self.client.get_problem_by_id(subject.get_uid(), task_id)
        return Task(
            response["id"],
            subject,
            response["topic"],
            response["condition"]["text"],
            response["condition"]["images"],
            response["url"],
            response["answer"]
        )
