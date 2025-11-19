import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated, Iterator, Union

from fastapi import APIRouter, Depends, FastAPI
from starlette.requests import Request
from typing_extensions import TypeAlias

from ncae_sdk._async.client import AsyncClient
from ncae_sdk._sync.client import Client
from ncae_sdk._types import ParamProcessorContext, _extract_class_type


class DependencyMixin:
    pass


def annotate_fastapi_dependencies(ctx: ParamProcessorContext) -> Iterator[inspect.Parameter]:
    for param in ctx.current:
        original_param = ctx.original_map[param.name]
        param_class = _extract_class_type(original_param.annotation)
        if param_class and issubclass(param_class, DependencyMixin):
            yield param.replace(annotation=Annotated[param.annotation, Depends()])
        else:
            yield param


def get_thread_pool(request: Request) -> ThreadPoolExecutor:
    thread_pool = getattr(request.state, "thread_pool", None)
    if not isinstance(thread_pool, ThreadPoolExecutor):
        raise RuntimeError("Thread pool not found in request state.")

    return thread_pool


def get_ncae_client_sync(request: Request) -> Client:
    sync_client = getattr(request.state, "ncae_client_sync")
    if not isinstance(sync_client, Client):
        raise RuntimeError("NcaeClient not found in request state.")

    return sync_client


def get_ncae_client_async(request: Request) -> AsyncClient:
    async_client = getattr(request.state, "ncae_client_async")
    if not isinstance(async_client, AsyncClient):
        raise RuntimeError("NcaeClient not found in request state.")

    return async_client


ThreadPoolExecutorDep: TypeAlias = Annotated[ThreadPoolExecutor, Depends(get_thread_pool)]
NcaeClientDep: TypeAlias = Annotated[Client, Depends(get_ncae_client_sync)]
AsyncNcaeClientDep: TypeAlias = Annotated[AsyncClient, Depends(get_ncae_client_async)]
Router: TypeAlias = Union[FastAPI, APIRouter]
