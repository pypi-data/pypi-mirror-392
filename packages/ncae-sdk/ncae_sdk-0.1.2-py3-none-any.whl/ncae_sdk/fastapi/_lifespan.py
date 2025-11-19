from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI

from ncae_sdk._async.client import AsyncClient
from ncae_sdk._auth import SessionAuth
from ncae_sdk._sync.client import Client
from ncae_sdk.fastapi._config import get_settings


class LifespanState(TypedDict):
    ncae_client_sync: Client
    ncae_client_async: AsyncClient
    thread_pool: ThreadPoolExecutor


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[LifespanState]:
    # Startup
    settings = get_settings()
    ncae_auth = SessionAuth(username=settings.ncae_username, password=settings.ncae_password)
    ncae_client_sync = Client(
        base_url=settings.ncae_base_url,
        auth=ncae_auth,
        verify=settings.ncae_verify_tls,
    )
    ncae_client_async = AsyncClient(
        base_url=settings.ncae_base_url,
        auth=ncae_auth,
        verify=settings.ncae_verify_tls,
    )
    thread_pool = ThreadPoolExecutor()

    # Runtime
    state: LifespanState = {
        "ncae_client_sync": ncae_client_sync,
        "ncae_client_async": ncae_client_async,
        "thread_pool": thread_pool,
    }
    yield state

    # Shutdown
    thread_pool.shutdown()
    ncae_client_sync.close()
    await ncae_client_async.close()
