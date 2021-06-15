from enum import Enum
from typing import Any, Callable, Dict, Generic, Optional, Sequence, Type, Union

from botx import Collector, Message
from botx.dependencies.models import Depends, get_dependant
from botx.dependencies.solving import get_executor

from botx_fsm.markers import FSMStateMarker, undefined, unset
from botx_fsm.models import Key, Transition
from botx_fsm.storages.base import BaseStorage, StateInStorage
from botx_fsm.typing import EnumT


def _check_state_is_valid(
        target_state: Union[EnumT, FSMStateMarker], states: Type[EnumT],
) -> None:
    error = RuntimeError(
        "state should be on of {0} enum states or unset object, got {1}".format(
            states, target_state,
        ),
    )

    if isinstance(target_state, Enum):
        if target_state not in states:
            raise error
    elif target_state is not unset and target_state is not undefined:
        raise error


class FSM(Generic[EnumT]):
    # storage will be initialized by middleware
    # but in processed handler it will be available
    storage: BaseStorage[EnumT]

    def __init__(
            self,
            states: Type[EnumT],
            dependencies: Optional[Sequence[Depends]] = None,
            dependency_overrides_provider: Any = None,
    ) -> None:
        self.states = states
        self.collector = Collector(
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )
        self.transitions: Dict[EnumT, Transition] = {}

    def on(  # noqa: WPS211
            self,
            trigger_state: EnumT,
            on_success: Union[EnumT, FSMStateMarker] = undefined,
            on_success_handler: Optional[Callable] = None,
            on_failure: Union[EnumT, FSMStateMarker] = undefined,
            on_failure_handler: Optional[Callable] = None,
            dependencies: Optional[Sequence[Depends]] = None,
            dependency_overrides_provider: Any = None,
    ) -> Callable:
        def decorator(command_handler: Callable) -> Callable:
            states_name = self.states.__name__
            trigger_state_name = trigger_state.name

            if trigger_state in self.transitions:
                raise RuntimeError(
                    "handler for {0} state of {1} states was already registered".format(
                        trigger_state, self.states,
                    ),
                )

            _check_state_is_valid(trigger_state, self.states)
            _check_state_is_valid(on_success, self.states)
            _check_state_is_valid(on_failure, self.states)

            handler_name = f"state_{states_name}#{trigger_state_name}"
            self.collector.add_handler(
                handler=command_handler,
                body=handler_name,
                name=handler_name,
                include_in_status=False,
                dependencies=dependencies,
                dependency_overrides_provider=dependency_overrides_provider,
            )
            self.transitions[trigger_state] = Transition(
                handler_name,
                on_success,
                on_failure,
                get_executor(get_dependant(call=on_success_handler)) if on_success_handler else None,
                get_executor(get_dependant(call=on_failure_handler)) if on_failure_handler else None,
            )

            return command_handler

        return decorator

    async def get_state(self, key: Union[Key, Message]) -> StateInStorage:
        return await self.storage.get_state(_convert_to_key(key))

    async def change_state(self, key: Union[Key, Message], new_state: EnumT,
                           **kwargs: Any) -> None:
        if new_state not in self.states:
            raise RuntimeError(
                "new state should be one of states from FSM initialization",
            )

        await self.storage.change_state(_convert_to_key(key), new_state, **kwargs)

    async def unset_state(self, key: Union[Key, Message]) -> None:
        await self.storage.change_state(_convert_to_key(key), unset)


def _convert_to_key(key: Union[Key, Message]) -> Key:
    if isinstance(key, Message):
        return Key.from_message(key)

    return key
