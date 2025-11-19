from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    ChangeSchedule,
    ChangeScheduleCreate,
    ChangeScheduleCreateModel,
    ChangeScheduleFilter,
    ChangeScheduleFilterModel,
    ChangeScheduleUpdate,
    ChangeScheduleUpdateModel,
)


class AsyncChangeScheduleEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "workflow/v1/change-schedule"

    async def list(self, **filters: Unpack[ChangeScheduleFilter]) -> AsyncIterator[ChangeSchedule]:
        results = self._list(self.BASE_PATH, ChangeScheduleFilterModel, filters)
        return map_async(ChangeSchedule.parse_api, results)

    async def find(self, **filters: Unpack[ChangeScheduleFilter]) -> Optional[ChangeSchedule]:
        result = await self._get_by_filters(self.BASE_PATH, ChangeScheduleFilterModel, filters)
        return ChangeSchedule.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[ChangeSchedule]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return ChangeSchedule.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ChangeScheduleCreate]) -> ChangeSchedule:
        result = await self._create(self.BASE_PATH, ChangeScheduleCreateModel, payload)
        return ChangeSchedule.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ChangeScheduleUpdate]) -> ChangeSchedule:
        result = await self._update(self.BASE_PATH, rid, ChangeScheduleUpdateModel, payload)
        return ChangeSchedule.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
