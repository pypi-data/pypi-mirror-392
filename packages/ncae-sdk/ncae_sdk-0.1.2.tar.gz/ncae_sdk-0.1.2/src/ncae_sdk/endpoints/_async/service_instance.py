from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    ServiceInstance,
    ServiceInstanceCreate,
    ServiceInstanceCreateModel,
    ServiceInstanceFilter,
    ServiceInstanceFilterModel,
    ServiceInstanceUpdate,
    ServiceInstanceUpdateModel,
)


class AsyncServiceInstanceEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/service-instance"

    async def list(self, **filters: Unpack[ServiceInstanceFilter]) -> AsyncIterator[ServiceInstance]:
        results = self._list(self.BASE_PATH, ServiceInstanceFilterModel, filters)
        return map_async(ServiceInstance.parse_api, results)

    async def find(self, **filters: Unpack[ServiceInstanceFilter]) -> Optional[ServiceInstance]:
        result = await self._get_by_filters(self.BASE_PATH, ServiceInstanceFilterModel, filters)
        return ServiceInstance.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[ServiceInstance]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return ServiceInstance.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ServiceInstanceCreate]) -> ServiceInstance:
        result = await self._create(self.BASE_PATH, ServiceInstanceCreateModel, payload)
        return ServiceInstance.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ServiceInstanceUpdate]) -> ServiceInstance:
        result = await self._update(self.BASE_PATH, rid, ServiceInstanceUpdateModel, payload)
        return ServiceInstance.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
