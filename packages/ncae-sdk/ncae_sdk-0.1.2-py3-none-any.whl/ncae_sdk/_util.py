import inspect
from typing import Any, AsyncIterator, Callable, Iterator, Optional, TypeVar

T = TypeVar("T")
R = TypeVar("R")


map_sync = map


def ensure_callable_sync(func: Callable[..., Any]) -> None:
    if not callable(func):
        raise TypeError(f"Function {func.__name__} must be a callable (expected [def], got [{type(func).__name__}]).")
    if inspect.iscoroutinefunction(func):
        raise TypeError(f"Function {func.__name__} must be a regular function (expected [def], got [async def]).")


def ensure_callable_async(func: Callable[..., Any]) -> None:
    if not callable(func):
        raise TypeError(
            f"Function {func.__name__} must be a callable (expected [async def], got [{type(func).__name__}])."
        )
    if not inspect.iscoroutinefunction(func):
        raise TypeError(f"Function {func.__name__} must be a coroutine function (expected [async def], got [def]).")


def parse_env_bool(value: str) -> bool:
    value = value.lower().strip()
    if value in ("true", "1", "yes", "on"):
        return True
    elif value in ("false", "0", "no", "off"):
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value}")


def parse_env_int(value: str) -> int:
    try:
        return int(value.strip())
    except ValueError as e:
        raise ValueError(f"Invalid integer value: {value}") from e


async def map_async(func: Callable[[T], R], iterable: AsyncIterator[T]) -> AsyncIterator[R]:
    async for item in iterable:
        yield await func(item) if inspect.iscoroutinefunction(func) else func(item)


async def next_async(iterable: AsyncIterator[T], default: Optional[T] = None) -> Optional[T]:
    try:
        return await iterable.__anext__()
    except StopAsyncIteration:
        return None


def next_sync(iterable: Iterator[T], default: Optional[T] = None) -> Optional[T]:
    return next(iterable, default)


__all__ = [
    "parse_env_bool",
    "parse_env_int",
    "ensure_callable_sync",
    "map_sync",
    "next_sync",
    "ensure_callable_async",
    "map_async",
    "next_async",
]
