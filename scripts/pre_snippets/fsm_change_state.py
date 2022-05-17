# flake8: noqa
from enum import Enum, auto

from pybotx import Bot, HandlerCollector, IncomingMessage

from pybotx_fsm import FSMCollector


class LoginStates(Enum):
    enter_email = auto()
    enter_password = auto()


fsm = FSMCollector(LoginStates)
collector = HandlerCollector()


