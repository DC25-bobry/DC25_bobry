import os
from enum import Enum

import jinja2
from jinja2 import FileSystemLoader
from backend.src.utils.util_commands import get_app_root


class EmailGenerator:

    RECEIVED = 1
    APPROVED = 2
    REJECTED = 3
    NON_EXISTENT = 0

    def __init__(self):
        self._env = jinja2.Environment(
            loader=FileSystemLoader(get_app_root() / "backend/src/email/templates/", followlinks=True))
        self._templates = {EmailGenerator.RECEIVED: "template_received.html",
                           EmailGenerator.APPROVED: "template_approval.html",
                           EmailGenerator.REJECTED: "template_rejection.html",
                           EmailGenerator.NON_EXISTENT: "template_non_existent.html"}
        self._name: str = "<imię>"
        self._position: str = "<pozycja>"
        self._gender: str = "<plec>"
        self._template: int = EmailGenerator.RECEIVED

    def _get_context(self):
        return {"name": self._name,
                "position": self._position,
                "gender": self._gender}

    def set_name(self, name: str):
        self._name = name
        return self

    def set_position(self, position: str):
        self._position = position
        return self

    def set_gender(self, gender: str):
        if gender.upper() == "M":
            self._gender = "m"
        elif gender.upper() == "F":
            self._gender = "f"
        else:
            self._gender = "x"
        return self

    def set_template(self, template: int):
        if template not in self._templates.keys():
            raise RuntimeError("EmailGenerator: Unknown email template")
        self._template = template
        return self

    def generate(self) -> str:
        template = self._env.get_template(self._templates[self._template])
        context = self._get_context()
        return template.render(context)



