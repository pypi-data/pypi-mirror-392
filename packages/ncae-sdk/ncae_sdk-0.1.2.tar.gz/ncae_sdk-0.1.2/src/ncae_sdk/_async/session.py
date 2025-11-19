import logging
from contextlib import asynccontextmanager
from ssl import SSLContext, VerifyMode
from typing import Any, AsyncIterator, Final, Optional

from httpcore import AsyncConnectionPool
from httpx import AsyncBaseTransport, AsyncClient
from typing_extensions import Self, Unpack

from ncae_sdk import __version__
from ncae_sdk._auth import Auth
from ncae_sdk._error import NcaeHttpError
from ncae_sdk._http import RequestArgs, Response
from ncae_sdk._session import SessionContext

logger = logging.getLogger("ncae_sdk.session")


class AsyncSession:
    __slots__ = ("_auth", "_client", "_context", "_is_clone")

    def __init__(
        self,
        *,
        auth: Auth,
        context: SessionContext,
        client: AsyncClient,
        _is_clone: bool = False,
    ) -> None:
        self._auth: Final[Auth] = auth
        self._client: Final[AsyncClient] = client
        self._context: Final[SessionContext] = context or SessionContext()
        self._is_clone: Final[bool] = _is_clone

    @classmethod
    def create(
        cls,
        auth: Auth,
        base_url: str,
        timeout: int,
        verify: bool,
        httpx_transport: Optional[AsyncBaseTransport] = None,
    ) -> Self:
        return cls(
            auth=auth,
            context=SessionContext(),
            client=AsyncClient(
                base_url=cls._sanitize_base_url(base_url),
                headers={"User-Agent": f"ncae-sdk-python/{__version__}"},
                timeout=timeout,
                verify=verify,
                transport=httpx_transport,
            ),
        )

    @property
    def context(self) -> SessionContext:
        return self._context

    @property
    def base_url(self) -> str:
        return str(self._client.base_url)

    @property
    def auth(self) -> Auth:
        return self._auth

    @property
    def timeout(self) -> float:
        return self._client.timeout.connect or 0

    @property
    def verify(self) -> bool:
        httpx_pool = getattr(self._client._transport, "_pool", None)
        assert isinstance(httpx_pool, AsyncConnectionPool)
        assert isinstance(httpx_pool._ssl_context, SSLContext)
        return httpx_pool._ssl_context.verify_mode != VerifyMode.CERT_NONE

    def clone(self, context: Optional[SessionContext] = None) -> Self:
        return self.__class__(
            context=context or SessionContext.empty(),
            client=self._client,
            auth=self._auth,
            _is_clone=True,
        )

    async def close(self) -> None:
        if not self._is_clone:
            await self._client.aclose()

    async def get(self, url: str, **kwargs: Unpack[RequestArgs]) -> Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Unpack[RequestArgs]) -> Response:
        return await self.request("POST", url, **kwargs)

    async def patch(self, url: str, **kwargs: Unpack[RequestArgs]) -> Response:
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Unpack[RequestArgs]) -> Response:
        return await self.request("DELETE", url, **kwargs)

    async def request(
        self, method: str, url: str, *, _is_retry: bool = False, **kwargs: Unpack[RequestArgs]
    ) -> Response:
        logger.debug("Executing NCAE API request: %s %s", method, url)
        mapped_kwargs = self._map_httpx_kwargs(kwargs)
        native_response = await self._client.request(method=method, url=url, **mapped_kwargs)
        response = Response(native_response)

        if response.status_code == 401 and not _is_retry:
            await self._auth.async_authenticate(self)
            return await self.request(method=method, url=url, _is_retry=True, **kwargs)

        if not response.is_success:
            raise NcaeHttpError(response)

        return response

    @asynccontextmanager
    async def stream(self, method: str, url: str, **kwargs: Unpack[RequestArgs]) -> AsyncIterator[Response]:
        mapped_kwargs = self._map_httpx_kwargs(kwargs)
        for attempt in range(2):
            async with self._client.stream(method=method, url=url, **mapped_kwargs) as native_response:
                response = Response(native_response)
                if response.status_code == 401:
                    await self._auth.async_authenticate(self)
                    continue

                # If the response has an unexpected status code, read the whole body, then raise a regular error.
                # It's important to read the body at this point, otherwise NcaeHttpError is missing information.
                if not response.is_success:
                    await response.aread()
                    raise NcaeHttpError(response)

                # Break the loop after the first successful response.
                yield response
                break

    def _map_httpx_kwargs(self, kwargs: RequestArgs) -> dict[str, Any]:
        mapped_kwargs: dict[str, Any] = dict(kwargs.copy())
        mapped_kwargs["params"] = mapped_kwargs.pop("query", None)

        if self._context.request_headers:
            headers = mapped_kwargs.get("headers", {}).copy()
            headers.update(self._context.request_headers)
            mapped_kwargs["headers"] = headers

        return mapped_kwargs

    @classmethod
    def _sanitize_base_url(cls, base_url: str) -> str:
        base_url = base_url.strip().rstrip("/") + "/"
        if not base_url.endswith("/api/"):
            base_url += "api/"

        return base_url
