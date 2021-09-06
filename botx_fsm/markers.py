try:
    from typing import Final, final  # noqa: WPS433
except ImportError:
    # Python 3.7 don't have Final type
    from typing_extensions import Final, final  # type: ignore  # noqa: WPS433,WPS440


@final
class FSMStateMarker:
    """Class that will be used only as a mark for special FSM values."""


unset: Final = FSMStateMarker()  # if state should be removed
undefined: Final = FSMStateMarker()  # if state was not provided
