from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Service,
    ServiceCreate,
    ServiceCreateModel,
    ServiceFilter,
    ServiceFilterModel,
    ServiceUpdate,
    ServiceUpdateModel,
)


class AsyncServiceEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/service"

    async def list(self, **filters: Unpack[ServiceFilter]) -> AsyncIterator[Service]:
        results = self._list(self.BASE_PATH, ServiceFilterModel, filters)
        return map_async(Service.parse_api, results)

    async def find(self, **filters: Unpack[ServiceFilter]) -> Optional[Service]:
        result = await self._get_by_filters(self.BASE_PATH, ServiceFilterModel, filters)
        return Service.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Service]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Service.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ServiceCreate]) -> Service:
        result = await self._create(self.BASE_PATH, ServiceCreateModel, payload)
        return Service.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ServiceUpdate]) -> Service:
        result = await self._update(self.BASE_PATH, rid, ServiceUpdateModel, payload)
        return Service.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
