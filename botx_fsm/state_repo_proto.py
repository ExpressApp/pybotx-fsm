from typing import Any, Hashable, Optional

from typing_extensions import Protocol


class StateRepoProto(Protocol):
    async def get(self, key: Hashable, default: Any = None) -> Any:
        ...

    async def set(
        self,
        key: Hashable,
        value: Any,
        expire: Optional[int] = None,
    ) -> None:
        ...

    async def delete(self, key: Hashable) -> None:
        ...
