try:
    from typing import Final, final  # noqa: WPS433
except ImportError:
    # Python 3.7 don't have Final type
    from typing import TypeVar  # noqa: WPS433

    Final = TypeVar("Final")  # noqa: WPS440
    final = lambda x: x  # noqa: E731,WPS440,WPS111


@final
class FSMStateMarker:
    """Class that will be used only as a mark for special FSM values."""


unset: Final = FSMStateMarker()  # if state should be removed
undefined: Final = FSMStateMarker()  # if state was not provided
