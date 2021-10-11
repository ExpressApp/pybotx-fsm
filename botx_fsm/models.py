import json
from dataclasses import dataclass
from typing import Callable, Generic, NewType, Optional, Union
from uuid import UUID

from botx import Message

from botx_fsm.markers import FSMStateMarker, undefined
from botx_fsm.typing import EnumT


@dataclass
class Transition(Generic[EnumT]):
    handler_name: str
    on_success: Union[EnumT, FSMStateMarker] = undefined
    on_failure: Union[EnumT, FSMStateMarker] = undefined

    on_success_handler: Optional[Callable] = None
    on_failure_handler: Optional[Callable] = None

    def change_state_on_success(self) -> bool:
        return self.on_success is not undefined

    def change_state_on_failure(self) -> bool:
        return self.on_failure is not undefined


Host = NewType("Host", str)
BotID = NewType("BotID", UUID)
ChatID = NewType("ChatID", UUID)
UserHUID = NewType("UserHUID", UUID)


@dataclass
class Key:
    host: Host
    bot_id: BotID
    chat_id: ChatID
    user_huid: UserHUID

    def to_json(self) -> str:
        return json.dumps(
            {
                "host": self.host,
                "bot_id": str(self.bot_id),
                "chat_id": str(self.chat_id),
                "user_huid": str(self.user_huid),
            },
        )

    @classmethod
    def from_message(cls, message: Message) -> "Key":
        if message.user_huid is None or message.group_chat_id is None:
            raise RuntimeError(
                "message should be received from user and contain user_huid",
            )

        return cls(
            Host(message.host),
            BotID(message.bot_id),
            ChatID(message.group_chat_id),
            UserHUID(message.user_huid),
        )
