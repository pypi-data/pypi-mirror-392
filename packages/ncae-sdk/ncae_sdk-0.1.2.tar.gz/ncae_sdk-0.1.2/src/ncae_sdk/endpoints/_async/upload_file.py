from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import IO, Final, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    UploadFile,
    UploadFileCreate,
    UploadFileCreateModel,
    UploadFileFilter,
    UploadFileFilterModel,
    UploadFileUpdate,
    UploadFileUpdateModel,
)


class AsyncUploadFileEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "automation/v1/upload-file"

    async def list(self, **filters: Unpack[UploadFileFilter]) -> AsyncIterator[UploadFile]:
        results = self._list(self.BASE_PATH, UploadFileFilterModel, filters)
        return map_async(UploadFile.parse_api, results)

    async def find(self, **filters: Unpack[UploadFileFilter]) -> Optional[UploadFile]:
        result = await self._get_by_filters(self.BASE_PATH, UploadFileFilterModel, filters)
        return UploadFile.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[UploadFile]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return UploadFile.parse_api(result) if result else None

    async def update(self, rid: ResourceId, /, **payload: Unpack[UploadFileUpdate]) -> UploadFile:
        result = await self._update(self.BASE_PATH, rid, UploadFileUpdateModel, payload)
        return UploadFile.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)

    async def upload(self, file: IO[bytes], **payload: Unpack[UploadFileCreate]) -> UploadFile:
        result = await self._create_multipart(self.BASE_PATH, UploadFileCreateModel, payload, {"file": file})
        return UploadFile.parse_api(result)

    @asynccontextmanager
    async def download(
        self, rid: ResourceId, *, chunk_size: Optional[int] = None
    ) -> AsyncIterator[AsyncIterator[bytes]]:
        async with self._session.stream("GET", f"{self.BASE_PATH}/{rid}/download") as response:
            yield await response.aiter_bytes(chunk_size=chunk_size)
