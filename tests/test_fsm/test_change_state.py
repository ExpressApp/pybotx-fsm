import asyncio
from enum import Enum, auto
from typing import Callable
from unittest.mock import AsyncMock

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
from tests.state_repo import StateRepo


class EnumForTests(Enum):
    FIRST_STATE = auto()
    SECOND_STATE = auto()


@pytest.fixture
def first_handler() -> AsyncMock:
    async def process_first_state(message: IncomingMessage, bot: Bot) -> None:
        await message.state.fsm.change_state(EnumForTests.SECOND_STATE)

    return AsyncMock(wraps=process_first_state)


@pytest.fixture
def second_handler() -> AsyncMock:
    async def process_second_state(message: IncomingMessage, bot: Bot) -> None:
        await message.state.fsm.drop_state()

    return AsyncMock(wraps=process_second_state)


@pytest.fixture
def fsm(first_handler: AsyncMock, second_handler: AsyncMock) -> FSMCollector:
    fsm = FSMCollector(EnumForTests)

    fsm.on(EnumForTests.FIRST_STATE)(first_handler)
    fsm.on(EnumForTests.SECOND_STATE)(second_handler)

    return fsm


@pytest.fixture
def bot(fsm: FSMCollector, bot_account: BotAccountWithSecret) -> Bot:
    collector = HandlerCollector()

    @collector.command("/fsm", visible=False)
    async def fsm_handler(message: IncomingMessage, bot: Bot) -> None:
        await message.state.fsm.change_state(EnumForTests.FIRST_STATE)

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        return

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        middlewares=[FSMMiddleware([fsm], state_repo_key="state_repo")],
    )
    built_bot.state.state_repo = StateRepo()
    return built_bot


@mark.asyncio
async def test_changing_state_on_successful(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    first_handler: AsyncMock,
    second_handler: AsyncMock,
) -> None:
    # - Arrange -
    start_message = incoming_message_factory(body="/fsm")
    first_message = incoming_message_factory(body="text")
    second_message = incoming_message_factory(body="text")

    # - Act -
    async with lifespan_wrapper(bot) as bot:
        bot.async_execute_bot_command(start_message)
        await asyncio.sleep(0)
        bot.async_execute_bot_command(first_message)
        await asyncio.sleep(0)
        bot.async_execute_bot_command(second_message)
        await asyncio.sleep(0)

    # - Assert -
    first_handler.assert_awaited_once_with(first_message, bot)
    second_handler.assert_awaited_once_with(second_message, bot)
