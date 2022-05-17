# flake8: noqa
from enum import Enum, auto

from pybotx import Bot, IncomingMessage

from pybotx_fsm import FSMCollector


def check_user_exist(email: str) -> bool:
    pass


def login(email: str, password: str) -> None:
    pass


class IncorrectPasswordError(Exception):
    pass


class LoginStates(Enum):
    enter_email = auto()
    enter_password = auto()


fsm = FSMCollector(LoginStates)


