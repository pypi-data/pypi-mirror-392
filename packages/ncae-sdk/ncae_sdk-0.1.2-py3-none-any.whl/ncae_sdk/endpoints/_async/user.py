from typing import Any, AsyncIterator, Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    User,
    UserCreate,
    UserCreateModel,
    UserFilter,
    UserFilterModel,
    UserUpdate,
    UserUpdateModel,
)


class AsyncUserEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "admin/v1/user"

    async def list(self, **filters: Unpack[UserFilter]) -> AsyncIterator[User]:
        results = self._list(self.BASE_PATH, UserFilterModel, filters)
        return map_async(User.parse_api, results)

    async def find(self, **filters: Unpack[UserFilter]) -> Optional[User]:
        result = await self._get_by_filters(self.BASE_PATH, UserFilterModel, filters)
        return User.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[User]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return User.parse_api(result) if result else None

    async def create(self, **payload: Unpack[UserCreate]) -> User:
        result = await self._create(self.BASE_PATH, UserCreateModel, payload, preprocessor=self._preprocessor)
        return User.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[UserUpdate]) -> User:
        result = await self._update(self.BASE_PATH, rid, UserUpdateModel, payload, preprocessor=self._preprocessor)
        return User.parse_api(result)

    async def set_password(self, rid: ResourceId, password: str) -> None:
        await self._session.post(
            f"{self.BASE_PATH}/{rid}/set_password",
            json={"password": password, "repeat_password": password},
        )

    @staticmethod
    def _preprocessor(value: dict[str, Any]) -> dict[str, Any]:
        if password := value.get("password"):
            value["repeat_password"] = password
        if become_password := value.get("become_password"):
            value["repeat_become_password"] = become_password

        return value
