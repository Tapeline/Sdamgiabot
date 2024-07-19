import os

import imgkit
import requests
from sdamgia import SdamGIA
import bs4


class GIAClient(SdamGIA):
    def __init__(self, wkhtmltoimage_path: str = os.getenv("WKHTMLTOIMAGE_BIN")):
        super().__init__()
        self._cache = {}
        self._wkhtmltoimage_path = wkhtmltoimage_path

    def reset_cache(self):
        self._cache.clear()

    def get_category_by_id_all(self, subject, category_id):
        cache_key = f"s{subject}c{category_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        page = 1
        tasks = []
        while True:
            response = self.get_category_by_id(subject, category_id, page)
            if len(response) == 0:
                break
            tasks.extend(response)
            page += 1
        self._cache[cache_key] = tasks
        return tasks

    def get_problem_as_image(self, subject, problem_id, image_path):
        response = requests.get(f"{self._SUBJECT_BASE_URL[subject]}/problem?id={problem_id}")
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        main_div = soup.find("div", class_="prob_maindiv")
        problem_div = list(main_div.children)[0]
        problem_html = str(problem_div).replace(
            "/get_file?id=",
            f"{self._SUBJECT_BASE_URL[subject]}/get_file?id="
        )
        config = imgkit.config(wkhtmltoimage=self._wkhtmltoimage_path)
        imgkit.from_string(
            problem_html,
            image_path,
            config=config,
            options={
                "enable-local-file-access": None
            }
        )

    def get_problem_url(self, subject, problem_id):
        return f"{self._SUBJECT_BASE_URL[subject]}/problem?id={problem_id}"
