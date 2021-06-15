from enum import Enum
from typing import Union

from botx_fsm.markers import FSMStateMarker, undefined
from botx_fsm.typing import EnumT


class FlowError(Exception):
    def __init__(
        self,
        new_state: Union[EnumT, FSMStateMarker] = undefined,
        *,
        clear: bool = False,
    ) -> None:
        if not isinstance(new_state, Enum) and new_state is not undefined:
            raise RuntimeError("new state should be enum member")

        self.new_state = new_state
        self.clear = clear

    def new_state_defined(self) -> bool:
        return self.new_state is not undefined and not self.clear

    def __repr__(self) -> str:
        new_state_str = str(self.new_state)
        if self.new_state is undefined:
            new_state_str = "<will not change>"
        if self.clear:
            new_state_str = "<will be cleared>"

        return f"FlowError(new_state: {new_state_str})"
