import os

import jinja2
from jinja2 import FileSystemLoader
from backend.src.utils.util_commands import get_app_root


class EmailContext:
    def __init__(self):
        self._name: str = "<imię>"
        self._position: str = "<pozycja>"
        self._gender: str = "<plec>"

    def get(self):
        return {"name": self._name,
                "position": self._position,
                "gender": self._gender}

    def set_name(self, name: str):
        self._name = name

    def set_position(self, position: str):
        self._position = position

    def set_gender(self, gender: str):
        if gender.upper() == "M":
            self._gender = "m"
        elif gender.upper() == "F":
            self._gender = "f"
        else:
            self._gender = "x"


class EmailGenerator:
    def __init__(self):
        self._env = jinja2.Environment(loader=FileSystemLoader(get_app_root() / "backend/src/email/templates/", followlinks=True))
        self._templates = {"received": "template_received.html"}

    def generate_email(self, template:str, context:dict) -> str:
        if template not in self._templates.keys():
            raise RuntimeError("EmailGenerator: Unknown email template")

        template = self._env.get_template(self._templates[template])
        return template.render(context)


