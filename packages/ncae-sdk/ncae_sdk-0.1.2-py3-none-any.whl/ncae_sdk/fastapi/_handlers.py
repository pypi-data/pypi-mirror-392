import logging

from fastapi import Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from ncae_sdk.fastapi._utils import obtain_request_logger

default_logger = logging.getLogger("ncae_sdk")


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger = obtain_request_logger(request)
    for error in exc.errors():
        type_ = error.get("type", "unknown")
        message = error.get("msg", "Unknown validation error")
        location = ".".join(str(part) for part in error.get("loc", []))

        if location:
            logger.error("Validation failed at '%s': %s (type: %s)", location, message, type_)
        else:
            logger.error("Validation failed: %s (type: %s)", message, type_)

    return await request_validation_exception_handler(request, exc)
