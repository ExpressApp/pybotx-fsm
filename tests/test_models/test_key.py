import pytest
from botx import Bot, Message, MessageBuilder

from botx_fsm import Key


def test_key_raises_runtime_error_for_messages_where_user_is_not_specified(
    bot: Bot,
) -> None:
    builder = MessageBuilder()
    message = builder.message
    message.user.user_huid = None
    with pytest.raises(RuntimeError):
        Key.from_message(Message.from_dict(message.dict(), bot))
