from collections.abc import AsyncIterator
from typing import Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Transaction,
    TransactionCreate,
    TransactionCreateModel,
    TransactionFilter,
    TransactionFilterModel,
    TransactionUpdate,
    TransactionUpdateModel,
)


class AsyncTransactionEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/transaction"

    async def list(self, **filters: Unpack[TransactionFilter]) -> AsyncIterator[Transaction]:
        results = self._list(self.BASE_PATH, TransactionFilterModel, filters)
        return map_async(Transaction.parse_api, results)

    async def find(self, **filters: Unpack[TransactionFilter]) -> Optional[Transaction]:
        result = await self._get_by_filters(self.BASE_PATH, TransactionFilterModel, filters)
        return Transaction.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Transaction]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Transaction.parse_api(result) if result else None

    async def create(self, **payload: Unpack[TransactionCreate]) -> Transaction:
        result = await self._create(self.BASE_PATH, TransactionCreateModel, payload)
        return Transaction.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[TransactionUpdate]) -> Transaction:
        result = await self._update(self.BASE_PATH, rid, TransactionUpdateModel, payload)
        return Transaction.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)
