import functools
import inspect
from typing import Callable, Final, Generic, Iterator, Optional, TypeVar

from typing_extensions import Concatenate, ParamSpec

from ncae_sdk.fastapi.runner._progress import ProgressHookAsync, ProgressHookSync, ProgressTracker, ProgressUpdate
from ncae_sdk.fastapi.runner._utils import ContextT, ItemT, RunnerResult

P = ParamSpec("P")
R = TypeVar("R")


class ParallelRunner(Generic[ContextT, ItemT]):
    def __init__(
        self,
        ctx: ContextT,
        items: list[ItemT],
        hook_sync: ProgressHookSync,
        hook_async: ProgressHookAsync,
    ) -> None:
        self._ctx: Final[ContextT] = ctx
        self._items: Final[list[ItemT]] = items
        self._progress: Final[ProgressTracker] = ProgressTracker(len(self._items))
        self._hook_sync: Final[ProgressHookSync] = hook_sync
        self._hook_async: Final[ProgressHookAsync] = hook_async

    @property
    def progress(self) -> ProgressTracker:
        return self._progress

    def run_sync(
        self,
        func: Callable[Concatenate[ContextT, ItemT, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iterator[RunnerResult[ItemT, R]]:
        if not callable(func) or inspect.iscoroutinefunction(func):
            raise TypeError("The provided function must be a synchronous function.")

        @functools.wraps(func)
        def wrapper(item: ItemT) -> RunnerResult[ItemT, R]:
            update: Optional[ProgressUpdate] = None
            try:
                result = func(self._ctx, item, *args, **kwargs)
                update = self._progress.increment("succeeded")
                return RunnerResult(item=item, exception=None, raw_value=result)
            except Exception as exc:
                update = self._progress.increment("failed")
                return RunnerResult(item=item, exception=exc, raw_value=None)
            finally:
                try:
                    if update is not None:
                        self._hook_sync(update)
                except Exception as exc:
                    self._ctx.internal_logger.warning("Execution of progress hook failed: %s", exc)

        self._progress.reset()
        futures = [self._ctx.thread_pool.submit(wrapper, item) for item in self._items]
        for future in futures:
            yield future.result()

    def _process_item_sync(
        self,
        func: Callable[Concatenate[ContextT, ItemT, P], R],
        item: ItemT,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RunnerResult[ItemT, R]:
        update: Optional[ProgressUpdate] = None
        try:
            result = func(self._ctx, item, *args, **kwargs)
            update = self._progress.increment("succeeded")
            return RunnerResult(item=item, exception=None, raw_value=result)
        except Exception as exc:
            update = self._progress.increment("failed")
            return RunnerResult(item=item, exception=exc, raw_value=None)
        finally:
            try:
                if update is not None:
                    self._hook_sync(update)
            except Exception as exc:
                self._ctx.internal_logger.warning("Execution of progress hook failed: %s", exc)
