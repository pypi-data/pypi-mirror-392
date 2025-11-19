from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Favourite,
    FavouriteCreate,
    FavouriteCreateModel,
    FavouriteFilter,
    FavouriteFilterModel,
    FavouriteUpdate,
    FavouriteUpdateModel,
)


class AsyncFavouriteEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "dashboard/v1/favourite"

    async def list(self, **filters: Unpack[FavouriteFilter]) -> AsyncIterator[Favourite]:
        results = self._list(self.BASE_PATH, FavouriteFilterModel, filters, paginate=False)
        return map_async(Favourite.parse_api, results)

    async def find(self, **filters: Unpack[FavouriteFilter]) -> Optional[Favourite]:
        result = await self._get_by_filters(self.BASE_PATH, FavouriteFilterModel, filters)
        return Favourite.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Favourite]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Favourite.parse_api(result) if result else None

    async def create(self, **payload: Unpack[FavouriteCreate]) -> Favourite:
        result = await self._create(self.BASE_PATH, FavouriteCreateModel, payload)
        return Favourite.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[FavouriteUpdate]) -> Favourite:
        result = await self._update(self.BASE_PATH, rid, FavouriteUpdateModel, payload)
        return Favourite.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
