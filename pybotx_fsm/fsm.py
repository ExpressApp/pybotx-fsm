from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace
from typing import Any

from pybotx import IncomingMessage

from pybotx_fsm.state_repo_proto import StateRepoProto
from pybotx_fsm.templates import KEY_TEMPLATE


@dataclass
class FSMStateData:
    state: Enum
    storage: SimpleNamespace


class FSM:
    def __init__(self, state_repo: StateRepoProto, message: IncomingMessage):
        self._state_repo = state_repo
        self._message = message

    async def change_state(self, state: Enum, **kwargs: Any) -> None:
        await self._state_repo.set(
            KEY_TEMPLATE.format(
                host=self._message.bot.host,
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                user_huid=self._message.sender.huid,
            ),
            FSMStateData(state, SimpleNamespace(**kwargs)),
        )

    async def drop_state(self) -> None:
        await self._state_repo.delete(
            KEY_TEMPLATE.format(
                host=self._message.bot.host,
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                user_huid=self._message.sender.huid,
            ),
        )
