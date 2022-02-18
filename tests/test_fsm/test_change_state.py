from enum import Enum, auto

import pytest
from botx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    lifespan_wrapper,
)
from pytest import mark

from botx_fsm import FSMCollector, FSMMiddleware


class EnumForTests(Enum):
    STATE1 = auto()
    STATE2 = auto()


@pytest.fixture
def fsm() -> FSMCollector:
    fsm = FSMCollector(EnumForTests)

    @fsm.on(EnumForTests.STATE1)
    async def process_state1(message: IncomingMessage) -> None:
        await message.state.fsm.change_state(message, EnumForTests.STATE2)

    @fsm.on(EnumForTests.STATE2)
    async def process_state2(message: IncomingMessage) -> None:
        await message.state.fsm.drop_state(message)

    return fsm


@pytest.fixture()
def fsm_bot(fsm: FSMCollector, bot_account: BotAccountWithSecret) -> Bot:
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        middlewares=[FSMMiddleware([fsm], state_repo_key="redis_repo")],
    )

    return built_bot


@mark.asyncio
async def test_changing_state_on_successful(fsm_bot: Bot) -> None:
    ...
