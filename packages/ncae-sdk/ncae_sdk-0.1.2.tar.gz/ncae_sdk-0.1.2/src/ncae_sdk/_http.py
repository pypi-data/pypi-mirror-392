from collections.abc import AsyncIterator, Iterator, MutableMapping
from functools import cached_property
from typing import IO, Any, Final, Mapping, Optional, Union

from httpx import Request as HttpxRequest
from httpx import Response as HttpxResponse
from typing_extensions import NotRequired, TypedDict


class RequestArgs(TypedDict):
    data: NotRequired[Mapping[str, Any]]
    files: NotRequired[Mapping[str, IO[bytes]]]
    headers: NotRequired[MutableMapping[str, str]]
    query: NotRequired[MutableMapping[str, Union[str, list[str]]]]
    json: NotRequired[Any]


class Request:
    def __init__(self, _native: HttpxRequest) -> None:
        self._native: Final[HttpxRequest] = _native

    @property
    def url(self) -> str:
        return str(self._native.url)

    @property
    def query_params(self) -> dict[str, str]:
        return dict(self._native.url.params.items())


class Response:
    def __init__(self, _native: HttpxResponse) -> None:
        self.native: Final[HttpxResponse] = _native

    @property
    def is_success(self) -> bool:
        return self.native.is_success

    @property
    def status_code(self) -> int:
        return self.native.status_code

    @property
    def content(self) -> bytes:
        return self.native.content

    @property
    def text(self) -> str:
        return self.native.text

    @cached_property
    def request(self) -> Request:
        return Request(self.native.request)

    def json(self, **kwargs: Any) -> Any:
        return self.native.json(**kwargs)

    def iter_bytes(self, chunk_size: Optional[int] = None) -> Iterator[bytes]:
        return self.native.iter_bytes(chunk_size=chunk_size)

    async def aiter_bytes(self, chunk_size: Optional[int] = None) -> AsyncIterator[bytes]:
        return self.native.aiter_bytes(chunk_size=chunk_size)

    def read(self) -> bytes:
        return self.native.read()

    async def aread(self) -> bytes:
        return await self.native.aread()
