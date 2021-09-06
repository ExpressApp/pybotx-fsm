from uuid import UUID, uuid4

import pytest
from botx import Bot, BotXCredentials, TestClient

from botx_fsm.storages.redis import RedisStorage


@pytest.fixture
async def redis_storage(bot: Bot) -> RedisStorage:
    storage = RedisStorage("redis://localhost/0")

    await storage.init(bot)
    await storage.redis_pool.flushdb()

    yield storage

    await storage.redis_pool.flushdb()
    await storage.close(bot)


@pytest.fixture
def bot_id() -> UUID:
    return uuid4()


@pytest.fixture
def bot(bot_id) -> Bot:
    bot = Bot(
        bot_accounts=[
            BotXCredentials(host="cts.example.com", secret_key="secret", bot_id=bot_id)
        ]
    )

    return bot


@pytest.fixture
def client(bot: Bot) -> TestClient:
    with TestClient(bot) as client:
        yield client
