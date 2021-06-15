import pickle

import pytest
from botx import Bot, Message, MessageBuilder
from pytest import mark as m

from botx_fsm import Key
from botx_fsm.storages.redis import RedisStorage, _build_redis_key


@m.asyncio
async def test_raising_runtime_error_if_restored_value_is_not_enum(
    bot: Bot, redis_storage: RedisStorage
) -> None:
    builder = MessageBuilder()
    message = builder.message
    handler_message = Message.from_dict(message.dict(), bot)
    key = Key.from_message(handler_message)
    await redis_storage.redis_pool.set(_build_redis_key(key.to_json()), pickle.dumps(1))

    with pytest.raises(RuntimeError):
        await redis_storage.get_state(key)
