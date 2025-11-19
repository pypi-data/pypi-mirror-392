from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    InfluxSystem,
    InfluxSystemCreate,
    InfluxSystemCreateModel,
    InfluxSystemFilter,
    InfluxSystemFilterModel,
    InfluxSystemUpdate,
    InfluxSystemUpdateModel,
)


class AsyncInfluxSystemEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "observability/v1/influx-system"

    async def list(self, **filters: Unpack[InfluxSystemFilter]) -> AsyncIterator[InfluxSystem]:
        results = self._list(self.BASE_PATH, InfluxSystemFilterModel, filters)
        return map_async(InfluxSystem.parse_api, results)

    async def find(self, **filters: Unpack[InfluxSystemFilter]) -> Optional[InfluxSystem]:
        result = await self._get_by_filters(self.BASE_PATH, InfluxSystemFilterModel, filters)
        return InfluxSystem.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[InfluxSystem]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return InfluxSystem.parse_api(result) if result else None

    async def create(self, **payload: Unpack[InfluxSystemCreate]) -> InfluxSystem:
        result = await self._create(self.BASE_PATH, InfluxSystemCreateModel, payload)
        return InfluxSystem.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[InfluxSystemUpdate]) -> InfluxSystem:
        result = await self._update(self.BASE_PATH, rid, InfluxSystemUpdateModel, payload)
        return InfluxSystem.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
