from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    GrafanaDashboard,
    GrafanaDashboardCreate,
    GrafanaDashboardCreateModel,
    GrafanaDashboardFilter,
    GrafanaDashboardFilterModel,
    GrafanaDashboardUpdate,
    GrafanaDashboardUpdateModel,
)


class AsyncGrafanaDashboardEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "observability/v1/grafana-dashboard"

    async def list(self, **filters: Unpack[GrafanaDashboardFilter]) -> AsyncIterator[GrafanaDashboard]:
        results = self._list(self.BASE_PATH, GrafanaDashboardFilterModel, filters)
        return map_async(GrafanaDashboard.parse_api, results)

    async def find(self, **filters: Unpack[GrafanaDashboardFilter]) -> Optional[GrafanaDashboard]:
        result = await self._get_by_filters(self.BASE_PATH, GrafanaDashboardFilterModel, filters)
        return GrafanaDashboard.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[GrafanaDashboard]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return GrafanaDashboard.parse_api(result) if result else None

    async def create(self, **payload: Unpack[GrafanaDashboardCreate]) -> GrafanaDashboard:
        result = await self._create(self.BASE_PATH, GrafanaDashboardCreateModel, payload)
        return GrafanaDashboard.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[GrafanaDashboardUpdate]) -> GrafanaDashboard:
        result = await self._update(self.BASE_PATH, rid, GrafanaDashboardUpdateModel, payload)
        return GrafanaDashboard.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
