from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, cast

from ncae_sdk.fastapi._context import BaseContext

T = TypeVar("T")
ItemT = TypeVar("ItemT")
ContextT = TypeVar("ContextT", bound=BaseContext)


@dataclass(frozen=True)
class RunnerResult(Generic[ItemT, T]):
    item: ItemT
    exception: Optional[Exception]
    raw_value: Optional[T]

    @property
    def ok(self) -> bool:
        return self.exception is None

    @property
    def value(self) -> T:
        if self.exception is not None:
            raise self.exception

        return cast(T, self.raw_value)
