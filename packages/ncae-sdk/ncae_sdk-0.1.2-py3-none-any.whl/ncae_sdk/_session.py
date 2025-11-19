from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from pydantic import computed_field
from typing_extensions import Self


@dataclass(frozen=True)
class SessionContext:
    ncae_tenant_id: Optional[int] = None
    ncae_transaction_id: Optional[str] = None
    extra_headers: Optional[dict[str, str]] = None

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def request_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.ncae_tenant_id is not None:
            headers["X-Tenant-Id"] = str(self.ncae_tenant_id)
        if self.ncae_transaction_id is not None:
            headers["X-Transaction-Id"] = self.ncae_transaction_id
        if self.extra_headers is not None:
            headers.update(self.extra_headers)

        return headers

    @classmethod
    def empty(cls) -> Self:
        return cls()
