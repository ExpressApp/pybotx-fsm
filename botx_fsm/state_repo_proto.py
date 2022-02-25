from typing import Any, Hashable, Optional

from typing_extensions import Protocol


class StateRepoProto(Protocol):
    async def get(self, key: Hashable, default: Any = None) -> Any:
        ...  # noqa: WPS428

    async def set(
        self,
        key: Hashable,
        value: Any,
        expire: Optional[int] = None,
    ) -> None:
        ...  # noqa: WPS428

    async def delete(self, key: Hashable) -> None:
        ...  # noqa: WPS428
