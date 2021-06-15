from typing import Sequence

from botx import Message
from botx.concurrency import callable_to_coroutine
from botx.middlewares.base import BaseMiddleware
from botx.typing import Executor

from botx_fsm.exceptions import FlowError
from botx_fsm.fsm import FSM, unset
from botx_fsm.models import Key
from botx_fsm.storages.base import BaseStorage, StateInStorage


class FSMMiddleware(BaseMiddleware):
    def __init__(
            self, executor: Executor, *, storage: BaseStorage,
            fsm_instances: Sequence[FSM],
    ) -> None:
        super().__init__(executor)
        self.fsm_instances = tuple(fsm_instances)
        self._storage = storage

        for fsm in fsm_instances:
            for state in fsm.states:
                if state not in fsm.transitions:
                    raise RuntimeError(
                        "unregistered handler for {0} state of {1} states".format(
                            state, fsm.states,
                        ),
                    )

            fsm.storage = storage

    async def dispatch(self, message: Message, call_next: Executor) -> None:
        try:
            current_state = await self._storage.get_state(Key.from_message(message))
        except RuntimeError:
            current_state = unset

        if current_state is unset:
            await callable_to_coroutine(call_next, message)
            return

        for fsm in self.fsm_instances:
            if isinstance(current_state.state, fsm.states):
                await self._process_fsm_state(current_state, fsm, message)
                return

        raise RuntimeError(
            "unable to find FSM for state from storage: {0}".format(current_state),
        )

    async def _process_fsm_state(
            self, current_state: StateInStorage, fsm: FSM, message: Message,
    ) -> None:
        key = Key.from_message(message)
        state_transitions = fsm.transitions[current_state.state]

        fsm_state_handler = fsm.collector.handler_for(state_transitions.handler_name)

        for attribute, argument in current_state.kwargs.items():
            setattr(message.state, attribute, argument)

        try:
            await fsm_state_handler(message)
        except FlowError as flow_error:
            if flow_error.clear:
                await self._storage.change_state(key, unset)
                return

            if flow_error.new_state_defined():
                if flow_error.new_state not in fsm.states:
                    raise RuntimeError(
                        "{0} state is not one of {1} enum values".format(
                            flow_error.new_state, fsm.states,
                        ),
                    )

                await self._storage.change_state(key, flow_error.new_state)

            return
        except Exception as any_error:
            if state_transitions.change_state_on_failure():
                await self._storage.change_state(key, state_transitions.on_failure)

            if state_transitions.on_failure_handler:
                await state_transitions.on_failure_handler(message)

            raise any_error

        if state_transitions.change_state_on_success():
            await self._storage.change_state(key, state_transitions.on_success)

        if state_transitions.on_success_handler:
            await state_transitions.on_success_handler(message)
