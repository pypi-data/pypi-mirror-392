from collections.abc import AsyncIterator
from typing import Final

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    UsageLog,
    UsageLogFilter,
    UsageLogFilterModel,
)


class AsyncUsageLogEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "logger/v1/usage-log"

    async def list(self, **filters: Unpack[UsageLogFilter]) -> AsyncIterator[UsageLog]:
        results = self._list(self.BASE_PATH, UsageLogFilterModel, filters)
        return map_async(UsageLog.parse_api, results)
