from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generic, Union

from botx import Bot

from botx_fsm.markers import FSMStateMarker
from botx_fsm.models import Key
from botx_fsm.typing import EnumT


@dataclass
class StateInStorage:
    state: Union[Enum, FSMStateMarker]
    kwargs: Dict[Any, Any]


class BaseStorage(Generic[EnumT]):
    async def init(self, _bot: Bot) -> None:
        """Optional callback to do async initialization stuff."""

    async def close(self, _bot: Bot) -> None:
        """Optional callback to do async finalization stuff."""

    async def get_state(self, key: Key) -> StateInStorage:
        raise NotImplementedError

    async def change_state(
        self, key: Key, state: Union[EnumT, FSMStateMarker], **kwargs: Any,
    ) -> None:
        raise NotImplementedError
