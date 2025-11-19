from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    CmdbEntry,
    CmdbEntryCreate,
    CmdbEntryCreateModel,
    CmdbEntryFilter,
    CmdbEntryFilterModel,
    CmdbEntryUpdate,
    CmdbEntryUpdateModel,
)


class AsyncCmdbEntryEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "cmdb/v1/entry"

    async def list(self, **filters: Unpack[CmdbEntryFilter]) -> AsyncIterator[CmdbEntry]:
        results = self._list(self.BASE_PATH, CmdbEntryFilterModel, filters)
        return map_async(CmdbEntry.parse_api, results)

    async def find(self, **filters: Unpack[CmdbEntryFilter]) -> Optional[CmdbEntry]:
        result = await self._get_by_filters(self.BASE_PATH, CmdbEntryFilterModel, filters)
        return CmdbEntry.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[CmdbEntry]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return CmdbEntry.parse_api(result) if result else None

    async def create(self, **payload: Unpack[CmdbEntryCreate]) -> CmdbEntry:
        result = await self._create(self.BASE_PATH, CmdbEntryCreateModel, payload)
        return CmdbEntry.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[CmdbEntryUpdate]) -> CmdbEntry:
        result = await self._update(self.BASE_PATH, rid, CmdbEntryUpdateModel, payload)
        return CmdbEntry.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
