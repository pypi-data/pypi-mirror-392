from ncae_sdk.__version__ import __description__, __title__, __version__
from ncae_sdk._async.client import AsyncClient
from ncae_sdk._auth import Auth, SessionAuth
from ncae_sdk._resource import ResourceId
from ncae_sdk._session import SessionContext
from ncae_sdk._sync.client import Client

__all__ = [
    # Re-exported classes and functions
    "AsyncClient",
    "Auth",
    "Client",
    "ResourceId",
    "SessionAuth",
    "SessionContext",
    "__description__",
    "__title__",
    "__version__",
    # Submodules
    "fastapi",
    "endpoints",
    "resources",
    "types",
]


__locals = locals()
for __name in __all__:
    if not __name.startswith("__") and __name in __locals:
        setattr(__locals[__name], "__module__", "ncae_sdk")
