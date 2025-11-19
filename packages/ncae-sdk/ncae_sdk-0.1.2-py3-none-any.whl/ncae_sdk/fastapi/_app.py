from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from ncae_sdk.fastapi import _handlers as handlers
from ncae_sdk.fastapi import _middlewares as middlewares
from ncae_sdk.fastapi._config import get_settings
from ncae_sdk.fastapi._lifespan import lifespan
from ncae_sdk.fastapi._logging import setup_default_logging
from ncae_sdk.fastapi._router import system_router


def create_module_app(
    title: str,
    version: str = "0.1.0",
) -> FastAPI:
    settings = get_settings()
    setup_default_logging(settings.debug)

    app = FastAPI(
        title=title,
        version=version,
        lifespan=lifespan,
        openapi_url="/api/schema.json",
        docs_url="/api/docs",
        redoc_url=None,
    )
    app.state.module_name = title
    app.state.module_version = version

    app.include_router(system_router)
    app.exception_handler(RequestValidationError)(handlers.validation_exception_handler)
    app.middleware("http")(middlewares.add_tracing_headers)
    app.middleware("http")(middlewares.inject_request_logger)
    app.middleware("http")(middlewares.log_http_request)

    return app
