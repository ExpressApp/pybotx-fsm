from enum import Enum, auto

from pybotx import Bot, HandlerCollector, IncomingMessage

from pybotx_fsm import FSMCollector


class FsmStates(Enum):
    INPUT_FIRST_NAME = auto()
    INPUT_LAST_NAME = auto()


collector = HandlerCollector()
fsm = FSMCollector(FsmStates)


