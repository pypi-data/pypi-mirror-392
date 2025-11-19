from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    PhaseInstance,
    PhaseInstanceCreate,
    PhaseInstanceCreateModel,
    PhaseInstanceFilter,
    PhaseInstanceFilterModel,
    PhaseInstanceUpdate,
    PhaseInstanceUpdateModel,
)


class AsyncPhaseInstanceEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/phase-instance"

    async def list(self, **filters: Unpack[PhaseInstanceFilter]) -> AsyncIterator[PhaseInstance]:
        results = self._list(self.BASE_PATH, PhaseInstanceFilterModel, filters)
        return map_async(PhaseInstance.parse_api, results)

    async def find(self, **filters: Unpack[PhaseInstanceFilter]) -> Optional[PhaseInstance]:
        result = await self._get_by_filters(self.BASE_PATH, PhaseInstanceFilterModel, filters)
        return PhaseInstance.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[PhaseInstance]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return PhaseInstance.parse_api(result) if result else None

    async def create(self, **payload: Unpack[PhaseInstanceCreate]) -> PhaseInstance:
        result = await self._create(self.BASE_PATH, PhaseInstanceCreateModel, payload)
        return PhaseInstance.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[PhaseInstanceUpdate]) -> PhaseInstance:
        result = await self._update(self.BASE_PATH, rid, PhaseInstanceUpdateModel, payload)
        return PhaseInstance.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
