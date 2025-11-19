from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Awaitable, Callable, DefaultDict, Final, Optional

from typing_extensions import TypeAlias


@dataclass(frozen=True)
class ProgressUpdate:
    elapsed_time: timedelta
    percentage: float
    current: int
    total: int


class ProgressTracker:
    STEP_MIN_PERCENTAGE_CHANGE: Final[int] = 1
    STEP_MIN_TIME_SINCE_MSECS: Final[int] = 1000

    def __init__(self, expected_total: int):
        self._lock: Final[Lock] = Lock()
        self._store: Final[DefaultDict[str, int]] = defaultdict(int)
        self._expected_total: Final[int] = expected_total
        self._last_update: datetime = datetime.now()
        self._last_percentage: float = 0
        self._start_time: Optional[datetime] = None

    def increment(self, key: str) -> Optional[ProgressUpdate]:
        with self._lock:
            self._store[key] += 1

        return self._check_for_update()

    def reset(self) -> None:
        with self._lock:
            self._store.clear()

    def _check_for_update(self) -> Optional[ProgressUpdate]:
        # Set start time on first increment
        if self._start_time is None:
            self._start_time = datetime.now()

        # Calculate current percentage and time since last update
        percentage = (self.current_total / self.expected_total) * 100
        time_delta = datetime.now() - self._last_update

        # Determine if eligible for progress update
        has_completed = self.current_total == self.expected_total
        has_enough_time = time_delta.total_seconds() * 1000 >= self.STEP_MIN_TIME_SINCE_MSECS
        has_enough_progress = percentage - self._last_percentage >= self.STEP_MIN_PERCENTAGE_CHANGE

        # Return progress update if either completed or enough progress/time has passed
        if not (has_completed or (has_enough_time and has_enough_progress)):
            return None

        return ProgressUpdate(
            elapsed_time=datetime.now() - self._start_time if self._start_time else timedelta(0),
            percentage=percentage,
            current=self.current_total,
            total=self.expected_total,
        )

    def __str__(self) -> str:
        return ", ".join(f"{key}={count}" for key, count in self._store.items())

    @property
    def current_total(self) -> int:
        return sum(self._store.values())

    @property
    def expected_total(self) -> int:
        return self._expected_total


ProgressHookSync: TypeAlias = Callable[[ProgressUpdate], None]
ProgressHookAsync: TypeAlias = Callable[[ProgressUpdate], Awaitable[None]]
