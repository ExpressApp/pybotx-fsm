import pickle
from datetime import timedelta
from enum import Enum
from typing import Any, Union

from cachetools import TTLCache

from botx_fsm import Key, unset
from botx_fsm.markers import FSMStateMarker
from botx_fsm.storages.base import BaseStorage, StateInStorage

ONE_WEEK = timedelta(weeks=1).total_seconds()
ONE_MB = 1024 * 1024


class MemoryStorage(BaseStorage):
    storage: TTLCache

    def __init__(self, maxsize: int = ONE_MB, expire_time: int = ONE_WEEK) -> None:
        self.storage = TTLCache(maxsize=maxsize, ttl=expire_time,)

    async def get_state(self, key: Key) -> StateInStorage:
        saved_value = self.storage.get(key.to_json())
        if saved_value is None:
            return unset

        restored_value = pickle.loads(saved_value)  # noqa: S301
        if not isinstance(restored_value, StateInStorage):
            raise RuntimeError("received not Enum instance from storage")

        return restored_value

    async def change_state(
        self, key: Key, state: Union[Enum, FSMStateMarker], **kwargs: Any
    ) -> None:
        memory_key = key.to_json()
        if state is unset:
            del self.storage[memory_key]
            return

        self.storage[memory_key] = pickle.dumps(
            StateInStorage(state=state, kwargs=kwargs)
        )
