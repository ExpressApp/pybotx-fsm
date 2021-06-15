from typing import Callable

from botx import Message, Bot


def _extractor(key: str) -> Callable[[Message], Bot]:
    def decorator(message: Message):
        try:
            return getattr(message.state, key)
        except AttributeError:
            return getattr(message.bot.state, key)

    return decorator


class _StateExtractor:
    def __getattribute__(self, item: str) -> Callable[[Message], Bot]:
        return _extractor(item)


StateExtractor = _StateExtractor()
