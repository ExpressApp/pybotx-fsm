from collections import namedtuple
from enum import Enum, auto
from uuid import UUID

from pybotx import Bot, BotAccountWithSecret, HandlerCollector

from pybotx_fsm import FSMCollector, FSMMiddleware


class LoginStates(Enum):
    enter_email = auto()
    enter_password = auto()


Module = namedtuple("Module", ("fsm", "collector"))

myfile = Module(FSMCollector(LoginStates), HandlerCollector())

