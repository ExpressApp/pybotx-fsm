from enum import Enum, auto
from collections.abc import Callable

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    lifespan_wrapper,
)

from pybotx_fsm import FSMCollector, FSMMiddleware
from tests.state_repo import StateRepo


async def test_getting_state(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    class EnumForTests(Enum):
        TEST_STATE = auto()

    collector = HandlerCollector()
    fsm = FSMCollector(EnumForTests)

    state: EnumForTests | None = None

    @fsm.on(EnumForTests.TEST_STATE)
    async def process_test_state(message: IncomingMessage, _: Bot) -> None:
        nonlocal state
        state = await message.state.fsm.get_state()

    @collector.command("/fsm", visible=False)
    async def fsm_handler(message: IncomingMessage, _: Bot) -> None:
        await message.state.fsm.change_state(EnumForTests.TEST_STATE)

    @collector.default_message_handler
    async def default_handler(_: IncomingMessage, __: Bot) -> None:
        ...  # noqa: WPS428

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        middlewares=[FSMMiddleware([fsm], state_repo_key="state_repo")],
    )
    built_bot.state.state_repo = StateRepo()

    init_message = incoming_message_factory(body="/fsm")
    first_message = incoming_message_factory(body="text")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(init_message)
        await bot.async_execute_bot_command(first_message)

    # - Assert -
    assert state == EnumForTests.TEST_STATE
