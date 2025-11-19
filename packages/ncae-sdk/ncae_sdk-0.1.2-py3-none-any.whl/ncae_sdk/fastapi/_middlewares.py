import time
from typing import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response

from ncae_sdk.fastapi._utils import obtain_request_logger

CallNext = Callable[[Request], Awaitable[Response]]


async def add_tracing_headers(request: Request, call_next: CallNext) -> Response:
    correlation_id = request.headers.get("X-Correlation-Id") or str(uuid4())
    request.state.correlation_id = correlation_id

    start_time = time.perf_counter()
    response = await call_next(request)
    response_time = time.perf_counter() - start_time

    response.headers["X-Correlation-Id"] = correlation_id
    response.headers["Server-Timing"] = f"request;dur={response_time:.3f}"

    return response


async def inject_request_logger(request: Request, call_next: CallNext) -> Response:
    obtain_request_logger(request, recreate=True)
    return await call_next(request)


async def log_http_request(request: Request, call_next: CallNext) -> Response:
    response = await call_next(request)
    if request.method in ["HEAD", "GET"] and request.url.path == "/api/system/healthz":
        return response

    logger = obtain_request_logger(request)
    logger.info(
        "%d %s %s from %s",
        response.status_code,
        request.method,
        request.url.path,
        request.client.host if request.client else "unknown",
    )

    return response
