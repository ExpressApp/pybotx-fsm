from typing import Any, Callable

from botx import Bot, Message


def _extractor(key: str) -> Callable[[Message], Bot]:
    def decorator(message: Message) -> Any:
        try:
            return getattr(message.state, key)
        except AttributeError:
            return getattr(message.bot.state, key)

    return decorator


class _StateExtractor:
    def __getattribute__(self, item: str) -> Callable[[Message], Bot]:  # noqa: WPS110
        return _extractor(item)


StateExtractor = _StateExtractor()
