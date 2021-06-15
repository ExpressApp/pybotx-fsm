import pytest
from botx import Bot, ExpressServer, TestClient

from botx_fsm.storages.redis import RedisStorage


@pytest.fixture
async def redis_storage() -> RedisStorage:
    storage = RedisStorage("redis://localhost/0")

    await storage.init()
    await storage.redis_pool.flushdb()

    yield storage

    await storage.redis_pool.flushdb()
    await storage.close()


@pytest.fixture
def bot() -> Bot:
    bot = Bot(known_hosts=[ExpressServer(host="cts.example.com", secret_key="secret")])

    return bot


@pytest.fixture
def client(bot: Bot) -> TestClient:
    with TestClient(bot) as client:
        yield client
