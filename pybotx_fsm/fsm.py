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
    def __init__(self, state_repo: StateRepoProto, message: IncomingMessage) -> None:
        self._state_repo = state_repo
        self._message = message

    async def change_state(
        self,
        state: Enum,
        *,
        ttl_seconds: int | None = None,
        **kwargs: Any,
    ) -> None:
        await self._state_repo.set(
            KEY_TEMPLATE.format(
                host=self._message.bot.host,
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                user_huid=self._message.sender.huid,
            ),
            FSMStateData(state, SimpleNamespace(**kwargs)),
            expire=ttl_seconds,
        )

    async def get_state(self) -> Enum | None:
        fsm_state_data: FSMStateData | None = await self._state_repo.get(
            KEY_TEMPLATE.format(
                host=self._message.bot.host,
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                user_huid=self._message.sender.huid,
            ),
        )

        if not fsm_state_data:
            return None

        return fsm_state_data.state

    async def drop_state(self) -> None:
        await self._state_repo.delete(
            KEY_TEMPLATE.format(
                host=self._message.bot.host,
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                user_huid=self._message.sender.huid,
            ),
        )
