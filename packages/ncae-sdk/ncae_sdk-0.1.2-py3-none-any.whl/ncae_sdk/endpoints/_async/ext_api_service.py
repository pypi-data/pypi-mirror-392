from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    ExtApiService,
    ExtApiServiceCreate,
    ExtApiServiceCreateModel,
    ExtApiServiceFilter,
    ExtApiServiceFilterModel,
    ExtApiServiceUpdate,
    ExtApiServiceUpdateModel,
)


class AsyncExtApiServiceEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/ext-api-service"

    async def list(self, **filters: Unpack[ExtApiServiceFilter]) -> AsyncIterator[ExtApiService]:
        results = self._list(self.BASE_PATH, ExtApiServiceFilterModel, filters)
        return map_async(ExtApiService.parse_api, results)

    async def find(self, **filters: Unpack[ExtApiServiceFilter]) -> Optional[ExtApiService]:
        result = await self._get_by_filters(self.BASE_PATH, ExtApiServiceFilterModel, filters)
        return ExtApiService.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[ExtApiService]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return ExtApiService.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ExtApiServiceCreate]) -> ExtApiService:
        result = await self._create(self.BASE_PATH, ExtApiServiceCreateModel, payload)
        return ExtApiService.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ExtApiServiceUpdate]) -> ExtApiService:
        result = await self._update(self.BASE_PATH, rid, ExtApiServiceUpdateModel, payload)
        return ExtApiService.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
