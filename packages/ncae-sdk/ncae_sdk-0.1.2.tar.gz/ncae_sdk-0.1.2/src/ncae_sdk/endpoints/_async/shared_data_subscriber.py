from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    SharedDataSubscriber,
    SharedDataSubscriberCreate,
    SharedDataSubscriberCreateModel,
    SharedDataSubscriberFilter,
    SharedDataSubscriberFilterModel,
    SharedDataSubscriberUpdate,
    SharedDataSubscriberUpdateModel,
)


class AsyncSharedDataSubscriberEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "shared_data/v1/subscriber"

    async def list(self, **filters: Unpack[SharedDataSubscriberFilter]) -> AsyncIterator[SharedDataSubscriber]:
        results = self._list(self.BASE_PATH, SharedDataSubscriberFilterModel, filters)
        return map_async(SharedDataSubscriber.parse_api, results)

    async def find(self, **filters: Unpack[SharedDataSubscriberFilter]) -> Optional[SharedDataSubscriber]:
        result = await self._get_by_filters(self.BASE_PATH, SharedDataSubscriberFilterModel, filters)
        return SharedDataSubscriber.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[SharedDataSubscriber]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return SharedDataSubscriber.parse_api(result) if result else None

    async def create(self, **payload: Unpack[SharedDataSubscriberCreate]) -> SharedDataSubscriber:
        result = await self._create(self.BASE_PATH, SharedDataSubscriberCreateModel, payload)
        return SharedDataSubscriber.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[SharedDataSubscriberUpdate]) -> SharedDataSubscriber:
        result = await self._update(self.BASE_PATH, rid, SharedDataSubscriberUpdateModel, payload)
        return SharedDataSubscriber.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
