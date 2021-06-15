from enum import Enum, auto

import pytest
from botx import Bot, Message, MessageBuilder, TestClient
from pytest import mark as m

from botx_fsm import FSM, FSMMiddleware, Key, unset
from botx_fsm.storages.redis import RedisStorage


class EnumForTests(Enum):
    state1 = auto()
    state2 = auto()


@pytest.fixture
def fsm() -> FSM[EnumForTests]:
    fsm = FSM(EnumForTests)

    @fsm.on(EnumForTests.state1)
    async def process_state1(message: Message) -> None:
        await fsm.change_state(message, EnumForTests.state2)

    @fsm.on(EnumForTests.state2)
    async def process_state2(message: Message) -> None:
        await fsm.unset_state(message)

    return fsm


@pytest.fixture()
def fsm_bot(bot: Bot, redis_storage: RedisStorage, fsm: FSM[EnumForTests]) -> Bot:
    bot.add_middleware(FSMMiddleware, storage=redis_storage, fsm_instances=[fsm])

    @bot.default
    async def default_handler(message: Message) -> None:
        await fsm.change_state(message, fsm.states.state1)

    return bot


@m.asyncio
async def test_changing_state_on_successful_execution(
    fsm_bot: Bot,
    fsm: FSM[EnumForTests],
    client: TestClient,
    redis_storage: RedisStorage,
) -> None:
    builder = MessageBuilder()
    message = builder.message
    handler_message = Message.from_dict(message.dict(), fsm_bot)

    await client.send_command(message)  # trigger initial state1
    await client.send_command(message)  # change to state2 manually
    assert await fsm.get_state(handler_message) == EnumForTests.state2

    await client.send_command(message)  # unset state
    assert await fsm.get_state(handler_message) == unset


@m.asyncio
async def test_fsm_accepts_key_as_argument(
    fsm_bot: Bot,
    fsm: FSM[EnumForTests],
    client: TestClient,
    redis_storage: RedisStorage,
) -> None:
    builder = MessageBuilder()
    message = builder.message
    handler_message = Message.from_dict(message.dict(), fsm_bot)
    key = Key.from_message(handler_message)

    await client.send_command(message)  # trigger initial state1
    await client.send_command(message)  # change to state2 manually
    assert await fsm.get_state(key) == EnumForTests.state2
