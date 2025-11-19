import functools
from traceback import TracebackException
from typing import Any, Awaitable, Callable

from fastapi import BackgroundTasks
from typing_extensions import Concatenate

from ncae_sdk._types import (
    FuncP,
    FuncR,
    inject_parameter,
    process_function_parameters,
    resolve_generic_signatures,
)
from ncae_sdk.fastapi._context import _run_async_or_sync_function
from ncae_sdk.fastapi._dependencies import Router, annotate_fastapi_dependencies
from ncae_sdk.fastapi.extapi._context import ExtApiPhaseContext
from ncae_sdk.types import PhaseStatus


def extapi_phase_route(
    router: Router, path: str
) -> Callable[
    [Callable[FuncP, Any]],
    Callable[Concatenate[ExtApiPhaseContext, BackgroundTasks, FuncP], Awaitable[None]],
]:
    def decorator(
        func: Callable[FuncP, Any],
    ) -> Callable[
        Concatenate[ExtApiPhaseContext, BackgroundTasks, FuncP],
        Awaitable[None],
    ]:
        @router.post(path, status_code=204)
        @process_function_parameters(
            resolve_generic_signatures,
            inject_parameter("__sdk_tasks", BackgroundTasks),
            inject_parameter("__sdk_context", ExtApiPhaseContext),
            annotate_fastapi_dependencies,
        )
        @_wrap_extapi_phase_handler
        @functools.wraps(func)
        async def wrapper(*args: FuncP.args, **kwargs: FuncP.kwargs) -> None:
            await _run_async_or_sync_function(func, *args, **kwargs)

        return wrapper

    return decorator


def extapi_report_route(
    router: Router, path: str
) -> Callable[
    [Callable[FuncP, FuncR]],
    Callable[FuncP, Awaitable[FuncR]],
]:
    def decorator(func: Callable[FuncP, FuncR]) -> Callable[FuncP, Awaitable[FuncR]]:
        @router.post(path)
        @process_function_parameters(
            resolve_generic_signatures,
            annotate_fastapi_dependencies,
        )
        @functools.wraps(func)
        async def wrapper(*args: FuncP.args, **kwargs: FuncP.kwargs) -> FuncR:
            return await _run_async_or_sync_function(func, *args, **kwargs)

        return wrapper

    return decorator


def _wrap_extapi_phase_handler(
    func: Callable[FuncP, Awaitable[None]],
) -> Callable[Concatenate[ExtApiPhaseContext, BackgroundTasks, FuncP], Awaitable[None]]:
    @functools.wraps(func)
    async def wrapper(
        __sdk_context: ExtApiPhaseContext,
        __sdk_tasks: BackgroundTasks,
        *args: FuncP.args,
        **kwargs: FuncP.kwargs,
    ) -> None:
        # Wrapper function to run the actual phase task in the background with basic error handling
        async def phase_task(*task_args: FuncP.args, **task_kwargs: FuncP.kwargs) -> None:
            # Catch and report exceptions during phase execution
            try:
                await func(*task_args, **task_kwargs)
            except Exception as exc:
                tb = TracebackException.from_exception(exc).format()
                await __sdk_context.async_log_error(f"Execution of {func.__name__} failed:\n{''.join(tb)}")
                await __sdk_context.async_update_phase_status(PhaseStatus.ERRORED)
                return

            # Set phase status by default if still stuck on ORDERED
            phase_status = await __sdk_context.async_get_phase_status()
            if phase_status in [PhaseStatus.ORDERED, PhaseStatus.UPDATING, PhaseStatus.RETIRING]:
                if __sdk_context.is_decommission:
                    await __sdk_context.async_update_phase_status(PhaseStatus.RETIRED)
                else:
                    await __sdk_context.async_update_phase_status(PhaseStatus.DEPLOYED)

        __sdk_tasks.add_task(phase_task, *args, **kwargs)

    return wrapper
