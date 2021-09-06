# use pickle here only for dumping and restore enums
# check on restoring that value is Enum instance is there

import pickle  # noqa: S403
from enum import Enum
from typing import Any, Optional, Union

from aioredis import Redis, create_redis_pool
from botx import Bot

from botx_fsm.markers import FSMStateMarker, unset
from botx_fsm.models import Key
from botx_fsm.storages.base import BaseStorage, StateInStorage

REDIS_PREFIX = "botx_fsm"


def _build_redis_key(key: str, prefix: str = REDIS_PREFIX) -> str:
    return ":".join((prefix, key))


class RedisStorage(BaseStorage):
    redis_pool: Redis

    def __init__(
        self,
        redis_dsn: str,
        prefix: str = REDIS_PREFIX,
        expire_time: Optional[int] = None,
    ) -> None:
        self.redis_dsn = redis_dsn
        self._prefix = prefix
        self._expire_time = expire_time

    async def init(self, _bot: Bot) -> None:
        self.redis_pool = await create_redis_pool(self.redis_dsn)

    async def close(self, _bot: Bot) -> None:
        self.redis_pool.close()
        await self.redis_pool.wait_closed()

    async def get_state(self, key: Key) -> StateInStorage:
        redis_key = _build_redis_key(key.to_json(), self._prefix)
        saved_value = await self.redis_pool.get(redis_key)
        if saved_value is None:
            return unset  # type: ignore

        restored_value = pickle.loads(saved_value)  # noqa: S301
        if not isinstance(restored_value, StateInStorage):
            raise RuntimeError("received not Enum instance from storage")

        return restored_value

    async def change_state(
        self, key: Key, state: Union[Enum, FSMStateMarker], **kwargs: Any,
    ) -> None:
        redis_key = _build_redis_key(key.to_json(), self._prefix)
        if state is unset:
            await self.redis_pool.delete(redis_key)
            return

        await self.redis_pool.set(
            redis_key,
            pickle.dumps(StateInStorage(state=state, kwargs=kwargs)),
            expire=self._expire_time,
        )
