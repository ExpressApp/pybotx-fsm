from enum import Enum, auto

from botx import Bot, Collector, Message

from botx_fsm import FSM, FlowError, unset


class Process1States(Enum):
    state1 = auto()
    state2 = auto()


collector = Collector()
fsm = FSM(Process1States)


@collector.handler(command="/start-process1")
async def start_process1_fsm(message: Message, bot: Bot) -> None:
    await bot.answer_message("started process 1; state 1", message)
    await fsm.change_state(message, Process1States.state1)


@fsm.on(Process1States.state1, on_success=Process1States.state2)
async def process_state1(message: Message, bot: Bot) -> None:
    await bot.answer_message("entered: {0}".format(message.body), message)
    if message.body == "to_state2":
        await bot.answer_message("go to process 1; state2", message)
        return

    await bot.answer_message("wrong text, try again", message)
    raise FlowError


@fsm.on(Process1States.state2, on_success=unset)
async def process_state2(message: Message, bot: Bot) -> None:
    await bot.answer_message("process1 completed", message)
