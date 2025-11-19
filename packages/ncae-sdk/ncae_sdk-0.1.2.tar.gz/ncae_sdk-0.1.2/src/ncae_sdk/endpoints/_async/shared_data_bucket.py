from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    SharedDataBucket,
    SharedDataBucketCreate,
    SharedDataBucketCreateModel,
    SharedDataBucketFilter,
    SharedDataBucketFilterModel,
    SharedDataBucketUpdate,
    SharedDataBucketUpdateModel,
)


class AsyncSharedDataBucketEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "shared_data/v1/bucket"

    async def list(self, **filters: Unpack[SharedDataBucketFilter]) -> AsyncIterator[SharedDataBucket]:
        results = self._list(self.BASE_PATH, SharedDataBucketFilterModel, filters)
        return map_async(SharedDataBucket.parse_api, results)

    async def find(self, **filters: Unpack[SharedDataBucketFilter]) -> Optional[SharedDataBucket]:
        result = await self._get_by_filters(self.BASE_PATH, SharedDataBucketFilterModel, filters)
        return SharedDataBucket.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[SharedDataBucket]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return SharedDataBucket.parse_api(result) if result else None

    async def create(self, **payload: Unpack[SharedDataBucketCreate]) -> SharedDataBucket:
        result = await self._create(self.BASE_PATH, SharedDataBucketCreateModel, payload)
        return SharedDataBucket.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[SharedDataBucketUpdate]) -> SharedDataBucket:
        result = await self._update(self.BASE_PATH, rid, SharedDataBucketUpdateModel, payload)
        return SharedDataBucket.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
