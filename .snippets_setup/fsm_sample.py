from enum import Enum, auto
from uuid import UUID

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, IncomingMessage

from pybotx_fsm import FSMCollector, FSMMiddleware

collector = HandlerCollector()


