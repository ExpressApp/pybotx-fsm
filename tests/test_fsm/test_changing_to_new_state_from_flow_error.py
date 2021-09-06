from enum import Enum, auto

import pytest
from botx import Bot, Message, MessageBuilder, TestClient
from pytest import mark as m

from botx_fsm import FSM, FlowError, FSMMiddleware, Key
from botx_fsm.storages.redis import RedisStorage


class EnumForTests(Enum):
    state1 = auto()
    state2 = auto()


@pytest.fixture
def fsm() -> FSM[EnumForTests]:
    fsm = FSM(EnumForTests)

    @fsm.on(EnumForTests.state1)
    async def process_state1() -> None:
        raise FlowError(EnumForTests.state2)

    @fsm.on(EnumForTests.state2)
    async def process_state2() -> None:
        """process state2"""

    return fsm


@pytest.fixture()
def fsm_bot(bot: Bot, redis_storage: RedisStorage, fsm: FSM[EnumForTests]) -> Bot:
    bot.add_middleware(FSMMiddleware, storage=redis_storage, fsm_instances=[fsm])

    @bot.default
    async def default_handler(message: Message) -> None:
        await fsm.change_state(message, fsm.states.state1)

    return bot


@m.asyncio
async def test_state_will_be_unset_if_flow_error_called_with_clear(
    fsm_bot: Bot, client: TestClient, redis_storage: RedisStorage, bot_id
) -> None:
    builder = MessageBuilder()
    builder.bot_id = bot_id
    message = builder.message
    key = Key.from_message(Message.from_dict(message.dict(), fsm_bot))

    await client.send_command(message)  # trigger initial state1
    await client.send_command(message)  # change to state2 from FlowError
    assert (await redis_storage.get_state(key)).state == EnumForTests.state2
