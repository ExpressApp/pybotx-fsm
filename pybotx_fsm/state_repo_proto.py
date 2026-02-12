from collections.abc import Hashable
from typing import Any, Protocol


class StateRepoProto(Protocol):
    async def get(self, key: Hashable, default: Any = None) -> Any: ...

    async def set(
        self,
        key: Hashable,
        value: Any,
        expire: int | None = None,
    ) -> None: ...

    async def delete(self, key: Hashable) -> None: ...
