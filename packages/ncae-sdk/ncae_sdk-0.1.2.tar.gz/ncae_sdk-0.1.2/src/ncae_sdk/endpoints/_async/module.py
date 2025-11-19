from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Module,
    ModuleCreate,
    ModuleCreateModel,
    ModuleFilter,
    ModuleFilterModel,
    ModuleUpdate,
    ModuleUpdateModel,
)


class AsyncModuleEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "admin/v1/module"

    async def list(self, **filters: Unpack[ModuleFilter]) -> AsyncIterator[Module]:
        results = self._list(self.BASE_PATH, ModuleFilterModel, filters)
        return map_async(Module.parse_api, results)

    async def find(self, **filters: Unpack[ModuleFilter]) -> Optional[Module]:
        result = await self._get_by_filters(self.BASE_PATH, ModuleFilterModel, filters)
        return Module.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Module]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Module.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ModuleCreate]) -> Module:
        result = await self._create(self.BASE_PATH, ModuleCreateModel, payload)
        return Module.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ModuleUpdate]) -> Module:
        result = await self._update(self.BASE_PATH, rid, ModuleUpdateModel, payload)
        return Module.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
