from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    DeviceModel,
    DeviceModelFilter,
    DeviceModelFilterModel,
)


class AsyncDeviceModelEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "dashboard/v1/device-model"

    async def list(self, **filters: Unpack[DeviceModelFilter]) -> AsyncIterator[DeviceModel]:
        results = self._list(self.BASE_PATH, DeviceModelFilterModel, filters)
        return map_async(DeviceModel.parse_api, results)

    async def find(self, **filters: Unpack[DeviceModelFilter]) -> Optional[DeviceModel]:
        result = await self._get_by_filters(self.BASE_PATH, DeviceModelFilterModel, filters)
        return DeviceModel.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[DeviceModel]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return DeviceModel.parse_api(result) if result else None
