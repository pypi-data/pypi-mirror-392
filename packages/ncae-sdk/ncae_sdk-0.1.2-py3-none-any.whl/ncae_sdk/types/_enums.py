import logging
from enum import Enum


class AuditLogAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"


class ChangeScheduleAction(Enum):
    DEPLOY = "deploy"
    DECOM = "decom"
    SHARED_DATA_UPDATE = "shared_data_update"


class ChangeScheduleInterval(Enum):
    YEARLY = 0
    MONTHLY = 1
    WEEKLY = 2
    DAILY = 3
    HOURLY = 4
    MINUTELY = 5


class ChangeScheduleStatus(Enum):
    RUNNING = "running"
    QUEUED = "queued"
    DONE = "done"


class ChangeScheduleExecutionStyle(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class ExtApiAuthType(Enum):
    BASIC = "Basic"
    BEARER = "Bearer"


class InfluxRetention(Enum):
    KEEP_1_HOUR = "1H"
    KEEP_1_DAY = "1D"
    KEEP_7_DAYS = "7D"
    KEEP_1_MONTH = "1M"
    KEEP_3_MONTHS = "3M"
    KEEP_6_MONTHS = "6M"
    KEEP_1_YEAR = "1Y"


class LogLevel(str, Enum):
    DEBUG = "DG"
    INFORMATIONAL = "IN"
    WARNING = "WA"
    ERROR = "ER"

    def to_native(self) -> int:
        mapping: dict[str, int] = {
            self.DEBUG: logging.DEBUG,
            self.INFORMATIONAL: logging.INFO,
            self.WARNING: logging.WARNING,
            self.ERROR: logging.ERROR,
        }

        return mapping.get(self, logging.INFO)


class ModuleType(Enum):
    AWX = "awx-based"


class PhaseStatus(Enum):
    DEPLOYED = "DE"
    ERRORED = "ER"
    ORDERED = "OR"
    PENDING_UPDATE = "PU"
    READY = "RA"
    RETIRED = "RE"
    RETIRING = "RI"
    UPDATING = "UP"


class ReportCategory(Enum):
    DEFAULT = "default"
    SYSTEM = "system"


class ServiceCategory(Enum):
    DEFAULT = "default"
    SYSTEM = "system"


class TagColor(Enum):
    RED = "#F44336"
    PINK = "#E91E63"
    PURPLE = "#9C27B0"
    DEEP_PURPLE = "#673AB7"
    INDIGO = "#3F51B5"
    BLUE = "#2196F3"
    LIGHT_BLUE = "#03A9F4"
    CYAN = "#00BCD4"
    TEAL = "#009688"
    GREEN = "#4CAF50"
    LIGHT_GREEN = "#8BC34A"
    LIME = "#CDDC39"
    YELLOW = "#FFEB3B"
    AMBER = "#FFC107"
    ORANGE = "#FF9800"


class UploadFileCategory(Enum):
    REGULAR = "regular"
    PYTHON_SCRIPT = "python-script"
    PYTHON_DEPENDENCIES = "python-dependencies"
