from ncae_sdk.fastapi.runner._parallel import ParallelRunner
from ncae_sdk.fastapi.runner._utils import RunnerResult

__all__ = [
    "ParallelRunner",
    "RunnerResult",
]


__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "ncae_sdk.fastapi.runner")
