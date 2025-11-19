from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Device,
    DeviceCreate,
    DeviceCreateModel,
    DeviceFilter,
    DeviceFilterModel,
    DeviceUpdate,
    DeviceUpdateModel,
)


class AsyncDeviceEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "dashboard/v1/device"

    async def list(self, **filters: Unpack[DeviceFilter]) -> AsyncIterator[Device]:
        results = self._list(self.BASE_PATH, DeviceFilterModel, filters)
        return map_async(Device.parse_api, results)

    async def find(self, **filters: Unpack[DeviceFilter]) -> Optional[Device]:
        result = await self._get_by_filters(self.BASE_PATH, DeviceFilterModel, filters)
        return Device.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Device]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Device.parse_api(result) if result else None

    async def create(self, **payload: Unpack[DeviceCreate]) -> Device:
        result = await self._create(self.BASE_PATH, DeviceCreateModel, payload)
        return Device.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[DeviceUpdate]) -> Device:
        result = await self._update(self.BASE_PATH, rid, DeviceUpdateModel, payload)
        return Device.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
