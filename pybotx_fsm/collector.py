from enum import Enum
from typing import Callable, Optional, Sequence, Set, Type

from pybotx import HandlerCollector, IncomingMessageHandlerFunc, Middleware

from pybotx_fsm.templates import COMMAND_NAME_TEMPLATE


class FSMCollector(HandlerCollector):
    def __init__(
        self,
        states_cls: Type[Enum],
        middlewares: Optional[Sequence[Middleware]] = None,
    ) -> None:
        super().__init__(middlewares=middlewares)

        self.states_cls = states_cls
        self.states: Set[Enum] = set()

    def on(
        self,
        state: Enum,
        middlewares: Optional[Sequence[Middleware]] = None,
    ) -> Callable[[IncomingMessageHandlerFunc], IncomingMessageHandlerFunc]:
        assert isinstance(
            state,
            self.states_cls,
        ), f"State {state} is not member of {self.states_cls}"

        self.states.add(state)

        return self.command(
            command_name=COMMAND_NAME_TEMPLATE.format(
                state_class_name=self.states_cls.__name__,
                state_name=state.name,
            ),
            visible=False,
            middlewares=middlewares,
        )
