"""
Use cases
"""

import os
import random
import uuid

import requests

from domain.entities import UserId, AbstractUserRepository, AbstractTaskRepository, AbstractTask


class Message:
    """Textual response (unused)"""
    def __init__(self, task: AbstractTask, text: str, image_urls: list[str]):
        self.task = task
        self.text = text
        self.image_urls = image_urls


class ImageMessage:
    """Response with image"""
    def __init__(self, task: AbstractTask, image: str, text: str, url: str):
        self.task = task
        self.image = image
        self.text = text
        self.url = url


class MessageImagePool:
    # pylint: disable=missing-function-docstring
    """Unused, subjected for removal"""
    def __init__(self, urls: list):
        self._pool_id = str(uuid.uuid4())
        self._pool_path = f"images_{self._pool_id}"
        self._urls = urls
        self.filenames = []
        os.mkdir(self._pool_path)

    def download(self):
        for url in self._urls:
            self.filenames.append(self._download_url(url))

    def _download_url(self, url):
        content = requests.get(url).content
        filename = f"{self._pool_path}/{uuid.uuid4()}.svg"
        with open(filename, "wb") as f:
            f.write(content)
        return filename

    def free(self):
        for file in self.filenames:
            os.remove(file)
        os.rmdir(self._pool_path)


def generate_task_for_user(user_id: UserId,
                           user_repo: AbstractUserRepository,
                           task_repo: AbstractTaskRepository,
                           as_image=False) -> Message | ImageMessage | None:
    """Generate task for given user out of given repos"""
    preferred_topics = user_repo.get_user_preferred_topics(user_id)
    if len(preferred_topics) == 0:
        return None
    random_topic = random.choice(preferred_topics)
    seen_tasks = user_repo.get_seen_tasks(user_id)
    subject = task_repo.get_subject(random_topic[0])
    task_types = task_repo.get_task_types_in_subject(subject)
    if len(task_types) < int(random_topic[1]):
        return None
    task_type = task_types[int(random_topic[1]) - 1]
    exclude = [x[1] for x in seen_tasks if x[0] == subject.get_uid()]
    task = task_repo.get_random_task(subject, task_type, exclude)
    if task is None:
        return None
    image_path = None
    if as_image:
        image_path = f"image_{uuid.uuid4()}.png"
    task.initialize(task_repo.get_client(), as_image=as_image, image_path=image_path)
    user_repo.mark_task_seen(user_id, subject.get_uid(), task.get_uid())
    if as_image:
        return ImageMessage(
            task,
            image_path,
            f"{subject.get_name()} / Тип {random_topic[1]} \n"
            f"Ответить: <code>/ans {subject.get_uid()}:{task.get_uid()} </code> ответ\n\n ",
            task.get_task_url()
        )
    return Message(
        task,
        f"{subject.get_name()} / Тип {random_topic[1]} \n"
        f"Ответить: <code>/ans {subject.get_uid()}:{task.get_uid()} </code> ответ\n\n "
        f"{task.get_text()}\n"
        f"<a href=\"{task.get_task_url()}\">Открыть на сайте</a>",
        task.get_image_urls()
    )


def check_answer_for_task(task_repo: AbstractTaskRepository,
                          subject_id: str, task_id: str,
                          answer: str) -> bool:
    """Check whether the answer is correct"""
    subj = task_repo.get_subject(subject_id)
    task = task_repo.get_task(subj, task_id)
    return task_repo.submit_solution(task, answer)
