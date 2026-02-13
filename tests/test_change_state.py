from enum import Enum, auto
from collections.abc import Callable
from unittest.mock import AsyncMock, Mock

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    lifespan_wrapper,
)

from pybotx_fsm import FSMCollector, FSMMiddleware
from pybotx_fsm.fsm import FSM
from tests.state_repo import StateRepo


async def test_changing_state_on_successful(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    first_handler_trigger = Mock()
    second_handler_trigger = Mock()
    default_handler_trigger = Mock()

    class EnumForTests(Enum):
        FIRST_STATE = auto()
        SECOND_STATE = auto()

    collector = HandlerCollector()
    fsm = FSMCollector(EnumForTests)

    @fsm.on(EnumForTests.FIRST_STATE)
    async def process_first_state(message: IncomingMessage, _: Bot) -> None:
        await message.state.fsm.change_state(EnumForTests.SECOND_STATE)
        first_handler_trigger()

    @fsm.on(EnumForTests.SECOND_STATE)
    async def process_second_state(message: IncomingMessage, _: Bot) -> None:
        await message.state.fsm.drop_state()
        second_handler_trigger()

    @collector.default_message_handler
    async def default_handler(_: IncomingMessage, __: Bot) -> None:
        default_handler_trigger()

    @collector.command("/fsm", visible=False)
    async def fsm_handler(message: IncomingMessage, _: Bot) -> None:
        await message.state.fsm.change_state(EnumForTests.FIRST_STATE)

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        middlewares=[FSMMiddleware([fsm], state_repo_key="state_repo")],
    )
    built_bot.state.state_repo = StateRepo()

    init_message = incoming_message_factory(body="/fsm")
    first_message = incoming_message_factory(body="text")
    second_message = incoming_message_factory(body="text")
    third_message = incoming_message_factory(body="text")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(init_message)
        await bot.async_execute_bot_command(first_message)
        await bot.async_execute_bot_command(second_message)
        await bot.async_execute_bot_command(third_message)

    # - Assert -
    assert first_handler_trigger.called
    assert second_handler_trigger.called
    assert default_handler_trigger.called


async def test_changing_state_with_ttl(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    class EnumForTests(Enum):
        TEST_STATE = auto()

    state_repo = AsyncMock()
    message = incoming_message_factory(body="text")
    fsm = FSM(state_repo=state_repo, message=message)

    await fsm.change_state(
        EnumForTests.TEST_STATE,
        ttl_seconds=300,
        payload="value",
    )

    assert state_repo.set.await_count == 1

    state_data = state_repo.set.await_args.args[1]
    assert state_data.state == EnumForTests.TEST_STATE
    assert state_data.storage.payload == "value"
    assert state_repo.set.await_args.kwargs["expire"] == 300
