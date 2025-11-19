from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    ChangeScheduleRun,
    ChangeScheduleRunCreate,
    ChangeScheduleRunCreateModel,
    ChangeScheduleRunFilter,
    ChangeScheduleRunFilterModel,
    ChangeScheduleRunUpdate,
    ChangeScheduleRunUpdateModel,
)


class AsyncChangeScheduleRunEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "workflow/v1/change-schedule-run"

    async def list(self, **filters: Unpack[ChangeScheduleRunFilter]) -> AsyncIterator[ChangeScheduleRun]:
        results = self._list(self.BASE_PATH, ChangeScheduleRunFilterModel, filters)
        return map_async(ChangeScheduleRun.parse_api, results)

    async def find(self, **filters: Unpack[ChangeScheduleRunFilter]) -> Optional[ChangeScheduleRun]:
        result = await self._get_by_filters(self.BASE_PATH, ChangeScheduleRunFilterModel, filters)
        return ChangeScheduleRun.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[ChangeScheduleRun]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return ChangeScheduleRun.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ChangeScheduleRunCreate]) -> ChangeScheduleRun:
        result = await self._create(self.BASE_PATH, ChangeScheduleRunCreateModel, payload)
        return ChangeScheduleRun.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ChangeScheduleRunUpdate]) -> ChangeScheduleRun:
        result = await self._update(self.BASE_PATH, rid, ChangeScheduleRunUpdateModel, payload)
        return ChangeScheduleRun.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
