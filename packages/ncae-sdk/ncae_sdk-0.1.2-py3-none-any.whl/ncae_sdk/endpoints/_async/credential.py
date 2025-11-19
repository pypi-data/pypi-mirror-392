from collections.abc import AsyncIterator
from typing import Any, Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    Credential,
    CredentialCreate,
    CredentialCreateModel,
    CredentialFilter,
    CredentialFilterModel,
    CredentialUpdate,
    CredentialUpdateModel,
)


class AsyncCredentialEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "dashboard/v1/credential"

    async def list(self, **filters: Unpack[CredentialFilter]) -> AsyncIterator[Credential]:
        results = self._list(self.BASE_PATH, CredentialFilterModel, filters)
        return map_async(Credential.parse_api, results)

    async def find(self, **filters: Unpack[CredentialFilter]) -> Optional[Credential]:
        result = await self._get_by_filters(self.BASE_PATH, CredentialFilterModel, filters)
        return Credential.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[Credential]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return Credential.parse_api(result) if result else None

    async def create(self, **payload: Unpack[CredentialCreate]) -> Credential:
        result = await self._create(
            self.BASE_PATH, CredentialCreateModel, payload, preprocessor=self._add_repeat_passwords
        )
        return Credential.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[CredentialUpdate]) -> Credential:
        result = await self._update(
            self.BASE_PATH, rid, CredentialUpdateModel, payload, preprocessor=self._add_repeat_passwords
        )
        return Credential.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)

    @staticmethod
    def _add_repeat_passwords(value: dict[str, Any]) -> dict[str, Any]:
        if password := value.get("password"):
            value["repeat_password"] = password
        if become_password := value.get("become_password"):
            value["repeat_become_password"] = become_password

        return value
