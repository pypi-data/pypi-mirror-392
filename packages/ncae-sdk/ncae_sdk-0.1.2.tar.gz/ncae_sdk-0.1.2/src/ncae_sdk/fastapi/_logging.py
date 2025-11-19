import logging
import logging.config
from typing import TYPE_CHECKING, Any, Callable, MutableMapping, Union

from typing_extensions import TypeAlias


def stdout_filter() -> Callable[[logging.LogRecord], bool]:
    return lambda record: record.levelno <= logging.INFO


def stderr_filter() -> Callable[[logging.LogRecord], bool]:
    return lambda record: record.levelno > logging.INFO


NCAE_LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(name)s: [%(levelname)-8s] %(message)s"},
    },
    "filters": {
        "stdout_filter": {"()": stdout_filter},
        "stderr_filter": {"()": stderr_filter},
    },
    "handlers": {
        "stdout": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ["stdout_filter"],
        },
        "stderr": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "filters": ["stderr_filter"],
        },
    },
    "root": {
        "handlers": ["stdout", "stderr"],
        "level": "INFO",
    },
    "loggers": {
        "asyncio": {"level": "WARNING"},
        "httpx": {"level": "WARNING"},
        "httpcore": {"level": "WARNING"},
        "uvicorn": {"level": "INFO"},
    },
}


def setup_default_logging(debug_mode: bool) -> None:
    config = NCAE_LOGGING_CONFIG.copy()
    if debug_mode:
        config["root"]["level"] = "DEBUG"

    logging.config.dictConfig(config)


# Workaround for proper type hinting of LoggerAdapter, as it varies between Python versions
# See https://github.com/python/typeshed/issues/7855 for more details
if TYPE_CHECKING:
    LoggerAdapter = logging.LoggerAdapter[logging.Logger]
else:
    LoggerAdapter = logging.LoggerAdapter

ContextLogger: TypeAlias = Union[logging.Logger, LoggerAdapter]


class ContextLogAdapter(LoggerAdapter):
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> tuple[str, MutableMapping[str, Any]]:
        assert isinstance(self.extra, dict)
        return "[%s] %s" % (self.extra["identifier"], msg), kwargs
