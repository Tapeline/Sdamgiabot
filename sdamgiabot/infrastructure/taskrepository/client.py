import os
from pathlib import Path

import imgkit
import requests
from PIL import Image
import PIL.ImageOps
from dishka import FromDishka
from sdamgia import SdamGIA
import bs4

from sdamgiabot.config import Config
from sdamgiabot.constants import RENDER_TEMPLATE, RENDER_PAGE_WIDTH


class GIAClient(SdamGIA):
    def __init__(self, config: FromDishka[Config]) -> None:
        super().__init__()
        self._cache: dict[str, list[str]] = {}
        self._wkhtmltoimage_path = config.wkhtmltoimage_path

    def reset_cache(self) -> None:
        self._cache.clear()

    def get_category_by_id_all(self, subject, category_id) -> list[str]:
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

    def get_problem_as_image(self, subject, problem_id, image_path) -> None:
        response = requests.get(
            f"{self._SUBJECT_BASE_URL[subject]}/problem?id={problem_id}"
        )
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        main_div = soup.find("div", class_="prob_maindiv")
        problem_div = list(main_div.children)[0]  # type: ignore
        problem_html = str(problem_div).replace(
            "/get_file?id=",
            f"{self._SUBJECT_BASE_URL[subject]}/get_file?id="
        )
        config = imgkit.config(wkhtmltoimage=self._wkhtmltoimage_path)
        imgkit.from_string(
            RENDER_TEMPLATE.format(
                problem_html
            ),
            image_path,
            css="style.css",
            config=config,
            options={
                "enable-local-file-access": None,
                "width": RENDER_PAGE_WIDTH
            }
        )
        image = Image.open(image_path)
        inverted_image = PIL.ImageOps.invert(image)
        inverted_image.save(image_path)

    def get_problem_url(self, subject, problem_id) -> str:
        return f"{self._SUBJECT_BASE_URL[subject]}/problem?id={problem_id}"


if __name__ == '__main__':
    client = GIAClient(Config())
    client.get_problem_as_image(
        "rus",
        "1218",
        "problem.png"
    )
