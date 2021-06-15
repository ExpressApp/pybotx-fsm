from typing import Awaitable, Callable, Sequence

from botx import Bot as BaseBot

from bot.processes import process1, process2
from botx_fsm import FSMMiddleware
from botx_fsm.storages.redis import RedisStorage

BotLifespanEvent = Callable[[], Awaitable[None]]


class Bot(BaseBot):
    startup_events: Sequence[BotLifespanEvent] = []
    shutdown_events: Sequence[BotLifespanEvent] = []

    async def start(self) -> None:
        for event in self.startup_events:
            await event()

    async def shutdown(self) -> None:
        for event in self.shutdown_events:
            await event()

        await super().shutdown()


redis_storage = RedisStorage(redis_dsn="redis://localhost/0")

bot = Bot()
bot.add_middleware(
    FSMMiddleware, storage=redis_storage, fsm_instances=[process1.fsm, process2.fsm],
)

bot.startup_events = [redis_storage.init]
bot.shutdown_events = [redis_storage.close]

bot.include_collector(process1.collector)
bot.include_collector(process2.collector)
