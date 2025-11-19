from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    AuditLog,
    AuditLogFilter,
    AuditLogFilterModel,
)


class AsyncAuditLogEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "audit_log/v1/audit_log"

    async def list(self, **filters: Unpack[AuditLogFilter]) -> AsyncIterator[AuditLog]:
        results = self._list(self.BASE_PATH, AuditLogFilterModel, filters)
        return map_async(AuditLog.parse_api, results)

    async def find(self, **filters: Unpack[AuditLogFilter]) -> Optional[AuditLog]:
        result = await self._get_by_filters(self.BASE_PATH, AuditLogFilterModel, filters)
        return AuditLog.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[AuditLog]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return AuditLog.parse_api(result) if result else None
