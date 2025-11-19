from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from ncae_sdk._http import Response


class NcaeHttpError(Exception):
    def __init__(self, response: "Response") -> None:
        self.url: Final[str] = str(response.request.url)
        self.status_code: Final[int] = response.status_code
        self.content: Final[str] = response.content.decode("utf-8", errors="replace")
        super().__init__(
            f"Request to [{self.url}] failed with status code {self.status_code} and content: {self.content}"
        )
