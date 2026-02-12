from collections.abc import Callable, Sequence
from enum import Enum

from pybotx import HandlerCollector, IncomingMessageHandlerFunc, Middleware

from pybotx_fsm.templates import COMMAND_NAME_TEMPLATE


class FSMCollector(HandlerCollector):
    def __init__(
        self,
        states_cls: type[Enum],
        middlewares: Sequence[Middleware] | None = None,
    ) -> None:
        super().__init__(middlewares=middlewares)

        self.states_cls = states_cls
        self.states: set[Enum] = set()

    def on(
        self,
        state: Enum,
        middlewares: Sequence[Middleware] | None = None,
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
