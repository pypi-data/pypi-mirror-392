from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    ExtApiAuth,
    ExtApiAuthCreate,
    ExtApiAuthCreateModel,
    ExtApiAuthFilter,
    ExtApiAuthFilterModel,
    ExtApiAuthUpdate,
    ExtApiAuthUpdateModel,
)


class AsyncExtApiAuthEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/auth"

    async def list(self, **filters: Unpack[ExtApiAuthFilter]) -> AsyncIterator[ExtApiAuth]:
        results = self._list(self.BASE_PATH, ExtApiAuthFilterModel, filters)
        return map_async(ExtApiAuth.parse_api, results)

    async def find(self, **filters: Unpack[ExtApiAuthFilter]) -> Optional[ExtApiAuth]:
        result = await self._get_by_filters(self.BASE_PATH, ExtApiAuthFilterModel, filters)
        return ExtApiAuth.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[ExtApiAuth]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return ExtApiAuth.parse_api(result) if result else None

    async def create(self, **payload: Unpack[ExtApiAuthCreate]) -> ExtApiAuth:
        result = await self._create(self.BASE_PATH, ExtApiAuthCreateModel, payload)
        return ExtApiAuth.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[ExtApiAuthUpdate]) -> ExtApiAuth:
        result = await self._update(self.BASE_PATH, rid, ExtApiAuthUpdateModel, payload)
        return ExtApiAuth.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
