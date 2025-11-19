from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    GrafanaSystem,
    GrafanaSystemCreate,
    GrafanaSystemCreateModel,
    GrafanaSystemFilter,
    GrafanaSystemFilterModel,
    GrafanaSystemUpdate,
    GrafanaSystemUpdateModel,
)


class AsyncGrafanaSystemEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "observability/v1/grafana-system"

    async def list(self, **filters: Unpack[GrafanaSystemFilter]) -> AsyncIterator[GrafanaSystem]:
        results = self._list(self.BASE_PATH, GrafanaSystemFilterModel, filters)
        return map_async(GrafanaSystem.parse_api, results)

    async def find(self, **filters: Unpack[GrafanaSystemFilter]) -> Optional[GrafanaSystem]:
        result = await self._get_by_filters(self.BASE_PATH, GrafanaSystemFilterModel, filters)
        return GrafanaSystem.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[GrafanaSystem]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return GrafanaSystem.parse_api(result) if result else None

    async def create(self, **payload: Unpack[GrafanaSystemCreate]) -> GrafanaSystem:
        result = await self._create(self.BASE_PATH, GrafanaSystemCreateModel, payload)
        return GrafanaSystem.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[GrafanaSystemUpdate]) -> GrafanaSystem:
        result = await self._update(self.BASE_PATH, rid, GrafanaSystemUpdateModel, payload)
        return GrafanaSystem.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
