from enum import Enum, auto

import pytest

from botx_fsm import FlowError


class EnumForTests(Enum):
    state1 = auto()


def test_flow_error_raises_runtime_error_if_value_is_wrong() -> None:
    with pytest.raises(RuntimeError):
        FlowError(1)


def test_flow_error_representation_with_enum() -> None:
    error = FlowError(EnumForTests.state1)
    assert repr(error) == "FlowError(new_state: EnumForTests.state1)"


def test_flow_error_representation_with_unset() -> None:
    error = FlowError(clear=True)
    assert repr(error) == "FlowError(new_state: <will be cleared>)"


def test_flow_error_representation_with_undefined() -> None:
    error = FlowError()
    assert repr(error) == "FlowError(new_state: <will not change>)"
