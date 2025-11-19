from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Tenant,
    TenantFilter,
    TenantFilterModel,
)


class AsyncTenantEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "rbac/v1/tenant"

    async def list(self, **filters: Unpack[TenantFilter]) -> AsyncIterator[Tenant]:
        results = self._list(self.BASE_PATH, TenantFilterModel, filters)
        return map_async(Tenant.parse_api, results)

    async def get(self, rid: ResourceId) -> Optional[Tenant]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Tenant.parse_api(result) if result else None
