from enum import Enum, auto
from collections.abc import Callable
from unittest.mock import Mock

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    lifespan_wrapper,
)

from pybotx_fsm import FSMCollector, FSMMiddleware
from tests.state_repo import StateRepo


async def test_check_state(
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
    async def process_second_state(message: IncomingMessage, _: Bot) -> None:
        first_message = message.state.fsm_storage.first_message
        await message.state.fsm.change_state(
            EnumForTests.SECOND_STATE,
            first_message=first_message,
            second_message="Hello World!",
        )
        first_handler_trigger()

    @fsm.on(EnumForTests.SECOND_STATE)
    async def process_second_state(message: IncomingMessage, _: Bot) -> None:
        await message.state.fsm.drop_state()
        second_handler_trigger()

    @collector.default_message_handler
    async def default_handler(__: IncomingMessage, _: Bot) -> None:
        default_handler_trigger()

    @collector.command("/fsm", visible=False)
    async def fsm_handler(message: IncomingMessage, _: Bot) -> None:
        await message.state.fsm.change_state(
            EnumForTests.FIRST_STATE, first_message="Hello Friend!"
        )

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
    assert first_message.state.fsm_storage.first_message == "Hello Friend!"
    assert second_message.state.fsm_storage.first_message == "Hello Friend!"
    assert second_message.state.fsm_storage.second_message == "Hello World!"
    assert default_handler_trigger.called
