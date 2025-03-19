from typing import Callable, Optional
from uuid import UUID, uuid4

import pytest
from pybotx import (
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatTypes,
    IncomingMessage,
    UserDevice,
    UserSender,
)
from pydantic import AnyHttpUrl


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def user_huid() -> UUID:
    return UUID("6d4b5b6e-ae32-4988-be5d-47baa7100c66")


@pytest.fixture
def chat_id() -> UUID:
    return UUID("211c57d5-3439-4952-aa1d-729f70dd5871")


@pytest.fixture
def host() -> AnyHttpUrl:
    return AnyHttpUrl(url="https://cts.example.com", scheme="https")


@pytest.fixture
def bot_account(host: AnyHttpUrl, bot_id: UUID) -> BotAccountWithSecret:
    return BotAccountWithSecret(
        id=bot_id,
        cts_url=host,
        secret_key="bee001",
    )


@pytest.fixture
def incoming_message_factory(
    bot_id: UUID,
    user_huid: UUID,
    chat_id: UUID,
    host: str,
) -> Callable[..., IncomingMessage]:
    def factory(
        *,
        body: str = "",
        ad_login: Optional[str] = None,
        ad_domain: Optional[str] = None,
    ) -> IncomingMessage:
        return IncomingMessage(
            bot=BotAccount(
                id=bot_id,
                host=host,
            ),
            sync_id=uuid4(),
            source_sync_id=None,
            body=body,
            data={},
            metadata={},
            sender=UserSender(
                huid=user_huid,
                udid=None,
                ad_login=ad_login,
                ad_domain=ad_domain,
                username=None,
                is_chat_admin=True,
                is_chat_creator=True,
                device=UserDevice(
                    manufacturer=None,
                    device_name=None,
                    os=None,
                    pushes=None,
                    timezone=None,
                    permissions=None,
                    platform=None,
                    platform_package_id=None,
                    app_version=None,
                    locale=None,
                ),
            ),
            chat=Chat(
                id=chat_id,
                type=ChatTypes.PERSONAL_CHAT,
            ),
            raw_command=None,
        )

    return factory
