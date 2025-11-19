from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Tag,
    TagCreate,
    TagCreateModel,
    TagFilter,
    TagFilterModel,
    TagUpdate,
    TagUpdateModel,
)


class AsyncTagEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "tag/v1/tag"

    async def list(self, **filters: Unpack[TagFilter]) -> AsyncIterator[Tag]:
        results = self._list(self.BASE_PATH, TagFilterModel, filters)
        return map_async(Tag.parse_api, results)

    async def find(self, **filters: Unpack[TagFilter]) -> Optional[Tag]:
        result = await self._get_by_filters(self.BASE_PATH, TagFilterModel, filters)
        return Tag.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Tag]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Tag.parse_api(result) if result else None

    async def create(self, **payload: Unpack[TagCreate]) -> Tag:
        result = await self._create(self.BASE_PATH, TagCreateModel, payload)
        return Tag.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[TagUpdate]) -> Tag:
        result = await self._update(self.BASE_PATH, rid, TagUpdateModel, payload)
        return Tag.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
