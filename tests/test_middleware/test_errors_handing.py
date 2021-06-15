from enum import Enum, auto

import pytest
from botx import Bot, Message, MessageBuilder, TestClient
from pytest import mark as m

from botx_fsm import FSM, FlowError, FSMMiddleware, Key
from botx_fsm.storages.redis import RedisStorage


class EnumForTests(Enum):
    state = auto()


class WrongEnum(Enum):
    state = auto()


@pytest.fixture
def fsm() -> FSM[EnumForTests]:
    fsm = FSM(EnumForTests)

    @fsm.on(EnumForTests.state)
    async def process_state() -> None:
        """process state"""

    return fsm


@m.asyncio
async def test_raising_error_if_not_all_states_have_handlers(
    bot: Bot, client: TestClient, redis_storage: RedisStorage,
) -> None:
    fsm = FSM(EnumForTests)

    with pytest.raises(RuntimeError):
        bot.add_middleware(FSMMiddleware, storage=redis_storage, fsm_instances=[fsm])


@m.asyncio
async def test_raising_error_if_value_restored_from_storage_is_not_one_of_fsms(
    bot: Bot, fsm: FSM, client: TestClient, redis_storage: RedisStorage,
) -> None:
    builder = MessageBuilder()
    message = builder.message
    handler_message = Message.from_dict(message.dict(), bot)
    key = Key.from_message(handler_message)

    await redis_storage.change_state(key, WrongEnum.state)

    middleware = FSMMiddleware(bot, storage=redis_storage, fsm_instances=[fsm])

    with pytest.raises(RuntimeError):
        await middleware(handler_message)


@m.asyncio
async def test_raising_error_if_value_from_flow_error_is_not_from_fsm(
    bot: Bot, client: TestClient, redis_storage: RedisStorage,
) -> None:
    builder = MessageBuilder()
    message = builder.message
    handler_message = Message.from_dict(message.dict(), bot)
    key = Key.from_message(handler_message)

    fsm = FSM(EnumForTests)

    @fsm.on(EnumForTests.state)
    async def process_state() -> None:
        raise FlowError(WrongEnum.state)

    await redis_storage.change_state(key, EnumForTests.state)

    middleware = FSMMiddleware(bot, storage=redis_storage, fsm_instances=[fsm])

    with pytest.raises(RuntimeError):
        await middleware(handler_message)
