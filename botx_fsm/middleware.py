from typing import Optional, Sequence

from botx import Bot, HandlerCollector, IncomingMessage, IncomingMessageHandlerFunc

from botx_fsm.collector import FSMCollector
from botx_fsm.fsm import FSM, FSMStateData
from botx_fsm.state_repo_proto import StateRepoProto
from botx_fsm.templates import COMMAND_NAME_TEMPLATE, KEY_TEMPLATE


class FSMMiddleware:
    def __init__(
        self,
        collectors: Sequence[FSMCollector],
        *,
        state_repo_key: str,
    ) -> None:
        self._state_repo_key = state_repo_key

        self._ensure_no_orphan_states(collectors)

        self._collector = HandlerCollector()
        self._collector.include(*collectors)

    async def __call__(
        self,
        message: IncomingMessage,
        bot: Bot,
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        state_repo: StateRepoProto = getattr(bot.state, self._state_repo_key)

        message.state.fsm = FSM(state_repo, message)

        fsm_state_data: Optional[FSMStateData] = await state_repo.get(
            KEY_TEMPLATE.format(
                host=message.bot.host,
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                user_huid=message.sender.huid,
            ),
        )

        if fsm_state_data:
            state = fsm_state_data.state
            message.state.fsm_storage = fsm_state_data.storage
            await self._collector.handle_incoming_message_by_command(
                message,
                bot,
                command=COMMAND_NAME_TEMPLATE.format(
                    state_class_name=state.__class__.__name__,
                    state_name=state.name,
                ),
            )
        else:
            await call_next(message, bot)

    def _ensure_no_orphan_states(
        self,
        collectors: Sequence[FSMCollector],
    ) -> None:
        for collector in collectors:
            needed_states = set(collector.states_cls.__members__.values())
            unfilled_states = needed_states - collector.states
            assert unfilled_states == set(), (
                f"States {unfilled_states} have no "
                "FSMCollector.on decorated handlers"
            )
