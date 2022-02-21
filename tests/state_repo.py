from typing import Any, Hashable, Optional


class StateRepo:
    def __init__(self):
        self._storage = {}

    async def get(self, key: Hashable, default: Any = None) -> Any:
        return self._storage.get(key, default)

    async def set(
        self, key: Hashable, value: Any, expire: Optional[int] = None
    ) -> None:
        self._storage[key] = value

    async def delete(self, key: Hashable) -> None:
        self._storage.pop(key, None)
