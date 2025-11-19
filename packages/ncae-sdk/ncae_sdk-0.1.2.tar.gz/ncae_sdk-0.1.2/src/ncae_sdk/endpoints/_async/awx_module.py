from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    AwxModule,
    AwxModuleFilter,
    AwxModuleFilterModel,
    AwxModuleUpdate,
    AwxModuleUpdateModel,
)


class AsyncAwxModuleEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "admin/v1/awx-based-module"

    async def list(self, **filters: Unpack[AwxModuleFilter]) -> AsyncIterator[AwxModule]:
        results = self._list(self.BASE_PATH, AwxModuleFilterModel, filters)
        return map_async(AwxModule.parse_api, results)

    async def find(self, **filters: Unpack[AwxModuleFilter]) -> Optional[AwxModule]:
        result = await self._get_by_filters(self.BASE_PATH, AwxModuleFilterModel, filters)
        return AwxModule.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[AwxModule]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return AwxModule.parse_api(result) if result else None

    async def update(self, rid: ResourceId, /, **payload: Unpack[AwxModuleUpdate]) -> AwxModule:
        result = await self._update(self.BASE_PATH, rid, AwxModuleUpdateModel, payload)
        return AwxModule.parse_api(result)
