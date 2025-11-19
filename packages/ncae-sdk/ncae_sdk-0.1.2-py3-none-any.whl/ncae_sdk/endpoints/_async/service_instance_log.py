from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    ServiceInstanceLog,
    ServiceInstanceLogCreate,
    ServiceInstanceLogCreateModel,
    ServiceInstanceLogFilter,
    ServiceInstanceLogFilterModel,
    ServiceInstanceLogUpdate,
    ServiceInstanceLogUpdateModel,
)


class AsyncServiceInstanceLogEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "logger/v1/service-instance-log"

    async def list(self, **filters: Unpack[ServiceInstanceLogFilter]) -> AsyncIterator[ServiceInstanceLog]:
        results = self._list(self.BASE_PATH, ServiceInstanceLogFilterModel, filters)
        return map_async(ServiceInstanceLog.parse_api, results)

    async def find(self, **filters: Unpack[ServiceInstanceLogFilter]) -> Optional[ServiceInstanceLog]:
        result = await self._get_by_filters(self.BASE_PATH, ServiceInstanceLogFilterModel, filters)
        return ServiceInstanceLog.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[ServiceInstanceLog]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return ServiceInstanceLog.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ServiceInstanceLogCreate]) -> ServiceInstanceLog:
        result = await self._create(self.BASE_PATH, ServiceInstanceLogCreateModel, payload)
        return ServiceInstanceLog.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ServiceInstanceLogUpdate]) -> ServiceInstanceLog:
        result = await self._update(self.BASE_PATH, rid, ServiceInstanceLogUpdateModel, payload)
        return ServiceInstanceLog.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
