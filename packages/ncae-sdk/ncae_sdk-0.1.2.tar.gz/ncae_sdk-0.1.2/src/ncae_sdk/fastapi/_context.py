import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable, Callable, Final, Union, cast

from fastapi import Request
from pydantic import BaseModel, ConfigDict
from starlette.concurrency import run_in_threadpool

from ncae_sdk._async.client import AsyncClient
from ncae_sdk._session import SessionContext
from ncae_sdk._sync.client import Client
from ncae_sdk._types import FuncP, FuncR
from ncae_sdk.fastapi._dependencies import AsyncNcaeClientDep, NcaeClientDep, ThreadPoolExecutorDep
from ncae_sdk.fastapi._logging import ContextLogger
from ncae_sdk.fastapi._utils import obtain_request_logger


class EmptyModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        validate_by_name=False,
        validate_by_alias=True,
    )


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        serialize_by_alias=True,
        validate_by_name=True,
        validate_by_alias=False,
    )


class BaseContext:
    def __init__(
        self,
        request: Request,
        ncae_client: NcaeClientDep,
        async_ncae_client: AsyncNcaeClientDep,
        thread_pool: ThreadPoolExecutorDep,
    ):
        self._request: Final[Request] = request
        self._context: Final[SessionContext] = self._build_session_context()
        self._internal_logger: Final[ContextLogger] = obtain_request_logger(request)

        self._client: Final[Client] = ncae_client.clone_with_context(self._context)
        self._async_client: Final[AsyncClient] = async_ncae_client.clone_with_context(self._context)
        self._thread_pool: Final[ThreadPoolExecutor] = thread_pool

    @property
    def client(self) -> Client:
        return self._client

    @property
    def async_client(self) -> AsyncClient:
        return self._async_client

    @property
    def context(self) -> SessionContext:
        return self._context

    @property
    def internal_logger(self) -> ContextLogger:
        return self._internal_logger

    @property
    def thread_pool(self) -> ThreadPoolExecutor:
        return self._thread_pool

    def _build_session_context(self) -> SessionContext:
        return SessionContext()


async def _run_async_or_sync_function(
    func: Callable[FuncP, Union[FuncR, Awaitable[FuncR]]],
    /,
    *func_args: FuncP.args,
    **func_kwargs: FuncP.kwargs,
) -> FuncR:
    if inspect.iscoroutinefunction(func):
        async_func = cast(Callable[FuncP, Awaitable[FuncR]], func)
        return await async_func(*func_args, **func_kwargs)
    else:
        sync_func = cast(Callable[FuncP, FuncR], func)
        return await run_in_threadpool(sync_func, *func_args, **func_kwargs)
