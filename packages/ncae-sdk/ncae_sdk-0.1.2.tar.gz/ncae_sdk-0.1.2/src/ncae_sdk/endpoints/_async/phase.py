from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Phase,
    PhaseCreate,
    PhaseCreateModel,
    PhaseFilter,
    PhaseFilterModel,
    PhaseUpdate,
    PhaseUpdateModel,
)


class AsyncPhaseEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/phase"

    async def list(self, **filters: Unpack[PhaseFilter]) -> AsyncIterator[Phase]:
        results = self._list(self.BASE_PATH, PhaseFilterModel, filters)
        return map_async(Phase.parse_api, results)

    async def find(self, **filters: Unpack[PhaseFilter]) -> Optional[Phase]:
        result = await self._get_by_filters(self.BASE_PATH, PhaseFilterModel, filters)
        return Phase.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Phase]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Phase.parse_api(result) if result else None

    async def create(self, **payload: Unpack[PhaseCreate]) -> Phase:
        result = await self._create(self.BASE_PATH, PhaseCreateModel, payload)
        return Phase.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[PhaseUpdate]) -> Phase:
        result = await self._update(self.BASE_PATH, rid, PhaseUpdateModel, payload)
        return Phase.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
