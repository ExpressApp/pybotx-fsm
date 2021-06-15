from typing import Final, final


@final
class FSMStateMarker:
    """Class that will be used only as a mark for special FSM values."""


unset: Final = FSMStateMarker()  # if state should be removed
undefined: Final = FSMStateMarker()  # if state was not provided
