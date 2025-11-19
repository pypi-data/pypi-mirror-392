from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from ncae_sdk._async.session import AsyncSession
    from ncae_sdk._sync.session import Session


class Auth(ABC):
    @abstractmethod
    def authenticate(self, session: "Session") -> None:
        """Synchronously authenticate the session using the provided credentials."""
        ...

    @abstractmethod
    async def async_authenticate(self, session: "AsyncSession") -> None:
        """Asynchronously authenticate the session using the provided credentials."""
        ...


class SessionAuth(Auth):
    def __init__(self, username: str, password: str) -> None:
        if not username or not password:
            raise ValueError("Username and password must be provided for authentication.")

        self.username: Final[str] = username
        self.password: Final[str] = password

    def authenticate(self, session: "Session") -> None:
        session.post(
            "auth/v1/login/",
            json={
                "username": self.username,
                "password": self.password,
            },
        )

    async def async_authenticate(self, session: "AsyncSession") -> None:
        await session.post(
            "auth/v1/login/",
            json={
                "username": self.username,
                "password": self.password,
            },
        )
