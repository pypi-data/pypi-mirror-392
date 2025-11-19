from typing import AsyncIterator, Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Report,
    ReportCreate,
    ReportCreateModel,
    ReportFilter,
    ReportFilterModel,
    ReportUpdate,
    ReportUpdateModel,
)


class AsyncReportEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "dashboard/v1/onetimereport"

    async def list(self, **filters: Unpack[ReportFilter]) -> AsyncIterator[Report]:
        results = self._list(self.BASE_PATH, ReportFilterModel, filters)
        return map_async(Report.parse_api, results)

    async def find(self, **filters: Unpack[ReportFilter]) -> Optional[Report]:
        result = await self._get_by_filters(self.BASE_PATH, ReportFilterModel, filters)
        return Report.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Report]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Report.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ReportCreate]) -> Report:
        result = await self._create(self.BASE_PATH, ReportCreateModel, payload)
        return Report.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ReportUpdate]) -> Report:
        result = await self._update(self.BASE_PATH, rid, ReportUpdateModel, payload)
        return Report.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
