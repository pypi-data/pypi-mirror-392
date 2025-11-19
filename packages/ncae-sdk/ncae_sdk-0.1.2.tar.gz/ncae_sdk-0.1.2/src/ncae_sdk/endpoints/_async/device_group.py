from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    DeviceGroup,
    DeviceGroupCreate,
    DeviceGroupCreateModel,
    DeviceGroupFilter,
    DeviceGroupFilterModel,
    DeviceGroupUpdate,
    DeviceGroupUpdateModel,
)


class AsyncDeviceGroupEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "dashboard/v1/device-group"

    async def list(self, **filters: Unpack[DeviceGroupFilter]) -> AsyncIterator[DeviceGroup]:
        results = self._list(self.BASE_PATH, DeviceGroupFilterModel, filters)
        return map_async(DeviceGroup.parse_api, results)

    async def find(self, **filters: Unpack[DeviceGroupFilter]) -> Optional[DeviceGroup]:
        result = await self._get_by_filters(self.BASE_PATH, DeviceGroupFilterModel, filters)
        return DeviceGroup.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[DeviceGroup]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return DeviceGroup.parse_api(result) if result else None

    async def create(self, **payload: Unpack[DeviceGroupCreate]) -> DeviceGroup:
        result = await self._create(self.BASE_PATH, DeviceGroupCreateModel, payload)
        return DeviceGroup.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[DeviceGroupUpdate]) -> DeviceGroup:
        result = await self._update(self.BASE_PATH, rid, DeviceGroupUpdateModel, payload)
        return DeviceGroup.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
