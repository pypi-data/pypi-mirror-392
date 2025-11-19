import logging
from typing import Union, cast

from fastapi import Request
from pydantic import AliasChoices, AliasPath, BaseModel
from pydantic.fields import FieldInfo

from ncae_sdk.fastapi._logging import ContextLogAdapter, ContextLogger


def extract_pydantic_model_keys(
    model_cls: type[BaseModel],
    *,
    validate_by_name: bool = False,
    validate_by_alias: bool = True,
) -> set[str]:
    result: set[str] = set()
    for field_name, field in model_cls.model_fields.items():
        assert isinstance(field, FieldInfo)
        field_aliases = _extract_pydantic_field_keys(field.validation_alias)

        if validate_by_name:
            result.add(field_name)
        if validate_by_alias:
            result.update(field_aliases)

    return result


def _extract_pydantic_field_keys(value: Union[str, int, AliasPath, AliasChoices, None]) -> set[str]:
    if value is None:
        return set()

    if isinstance(value, (str, int)):
        return {str(value)}
    elif isinstance(value, AliasPath):
        return {str(value.path[0])}
    elif isinstance(value, AliasChoices):
        result: set[str] = set()
        for choice in value.choices:
            result.update(_extract_pydantic_field_keys(choice))

        return result
    else:
        raise TypeError(f"Unsupported alias type: {type(value)}")


def obtain_request_logger(request: Request, recreate: bool = False) -> ContextLogger:
    # Use existing logger from request state if available and not recreating
    logger = getattr(request.state, "logger", None)
    if isinstance(logger, (logging.Logger, logging.LoggerAdapter)) and not recreate:
        delattr(request.state, "logger")
        return logger

    # Obtain correlation ID, preferably from request state set by middleware, but falling back to headers
    # This is required in some cases as e.g. exception handlers do not pass through middleware
    base_logger = logging.getLogger("ncae_sdk.request")
    correlation_id = getattr(request.state, "correlation_id", None) or request.headers.get("X-Correlation-Id", None)
    if not correlation_id:
        return base_logger

    # Create and store a new ContextLogAdapter in request state
    request.state.logger = ContextLogAdapter(
        logger=base_logger,
        extra={"identifier": correlation_id},
    )

    return cast(ContextLogAdapter, request.state.logger)
