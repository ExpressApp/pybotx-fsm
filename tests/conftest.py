from typing import AsyncGenerator
from uuid import UUID

import httpx
import pytest
from botx import BotAccountWithSecret


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def host() -> str:
    return "cts.example.com"


@pytest.fixture
def bot_account(host: str, bot_id: UUID) -> BotAccountWithSecret:
    return BotAccountWithSecret(
        id=bot_id,
        host=host,
        secret_key="bee001",
    )


@pytest.fixture
async def httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client
