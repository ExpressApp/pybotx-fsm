from enum import Enum, auto
from typing import Any

import pytest
from botx import Bot, Message, MessageBuilder, TestClient
from pytest import mark as m

from botx_fsm import FSM, FSMMiddleware
from botx_fsm.storages.redis import RedisStorage


class EnumForTests(Enum):
    state1 = auto()


class WrongEnum(Enum):
    state = auto()


@pytest.fixture
def fsm() -> FSM[EnumForTests]:
    fsm = FSM(EnumForTests)

    @fsm.on(EnumForTests.state1)
    async def process_state1() -> None:
        """process state1"""

    return fsm


@pytest.fixture()
def fsm_bot(bot: Bot, redis_storage: RedisStorage, fsm: FSM[EnumForTests]) -> Bot:
    bot.add_middleware(FSMMiddleware, storage=redis_storage, fsm_instances=[fsm])

    return bot


@m.asyncio
async def test_raising_runtime_error_on_passing_wrong_enum(
    fsm_bot: Bot, fsm: FSM[EnumForTests],
) -> None:
    builder = MessageBuilder()
    message = builder.message
    handler_message = Message.from_dict(message.dict(), fsm_bot)

    with pytest.raises(RuntimeError):
        await fsm.change_state(handler_message, WrongEnum.state)


@m.asyncio
async def test_raising_runtime_error_on_duplicate_registration(
    fsm_bot: Bot,
    fsm: FSM[EnumForTests],
    client: TestClient,
    redis_storage: RedisStorage,
) -> None:
    with pytest.raises(RuntimeError):
        fsm.on(trigger_state=EnumForTests.state1,)(lambda: None)


@m.asyncio
@m.parametrize(
    "trigger_state, on_success_state, on_failure_state",
    (
        (WrongEnum.state, EnumForTests.state1, EnumForTests.state1),
        (EnumForTests.state1, WrongEnum.state, EnumForTests.state1),
        (EnumForTests.state1, EnumForTests.state1, WrongEnum.state),
        (EnumForTests.state1, object(), EnumForTests.state1),
        (EnumForTests.state1, EnumForTests.state1, object()),
    ),
)
async def test_raising_runtime_error_on_registering_state_on_wrong_value(
    bot: Bot, trigger_state: Any, on_success_state: Any, on_failure_state: Any,
) -> None:
    with pytest.raises(RuntimeError):
        FSM(EnumForTests).on(
            trigger_state=trigger_state,
            on_success=on_success_state,
            on_failure=on_failure_state,
        )(lambda: None)
