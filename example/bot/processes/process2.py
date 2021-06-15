from enum import Enum, auto

from botx import Bot, Collector, Message

from botx_fsm import FSM, FlowError, unset


class Process2States(Enum):
    state1 = auto()
    state2 = auto()
    state3 = auto()
    state4 = auto()


collector = Collector()
fsm = FSM(Process2States)


@collector.handler(command="/start-process2")
async def start_process1_fsm(message: Message, bot: Bot) -> None:
    await bot.answer_message("started process 2; state 1", message)
    await fsm.change_state(message, Process2States.state1)


@fsm.on(Process2States.state1, on_success=Process2States.state2)
async def process_state1(message: Message, bot: Bot) -> None:
    await bot.answer_message("entered: {0}".format(message.body), message)
    if message.body == "to_state2":
        await bot.answer_message("go to process 2; state2", message)
        return

    await bot.answer_message("wrong text, try again", message)
    raise FlowError


@fsm.on(
    Process2States.state2,
    on_success=Process2States.state3,
    on_failure=Process2States.state1,
)
async def process_state2(message: Message, bot: Bot) -> None:
    if message.body == "fail_this_step":
        await bot.answer_message("fail state2; go to process 2; state1", message)
        raise FlowError

    await bot.answer_message("go to process 2; state3", message)


@fsm.on(Process2States.state3, on_success=Process2States.state4)
async def process_state3(message: Message, bot: Bot) -> None:
    if message.body == "to_state1":
        await bot.answer_message("go to process 2; state1", message)
        raise FlowError(Process2States.state1)

    if message.body == "to_state2":
        await bot.answer_message("go to process 2; state2", message)
        raise FlowError(Process2States.state2)

    if message.body == "stop_this_process":
        await bot.answer_message("stop this process", message)
        raise FlowError(clear=True)

    await bot.answer_message("go to process 2; state4", message)


@fsm.on(Process2States.state4, on_success=unset, on_failure=Process2States.state1)
async def process_state4(message: Message, bot: Bot) -> None:
    await bot.answer_message("process2 completed", message)
