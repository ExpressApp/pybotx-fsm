from enum import Enum, auto
from uuid import UUID

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, IncomingMessage

from pybotx_fsm import FSMCollector, FSMMiddleware

collector = HandlerCollector()


@collector.command("/echo", description="Echo command")
async def help_command(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(FsmStates.EXAMPLE_STATE)
    await bot.answer_message("Input your text:")


