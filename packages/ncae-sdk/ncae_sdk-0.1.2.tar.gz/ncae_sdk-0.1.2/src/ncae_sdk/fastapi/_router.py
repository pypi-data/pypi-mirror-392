from fastapi import APIRouter, FastAPI, Request
from starlette.responses import RedirectResponse

system_router = APIRouter(prefix="/api/system", tags=["system"])


@system_router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/api/docs")


@system_router.get("/healthz")
async def health_check(request: Request) -> dict[str, str]:
    app = request.app
    assert isinstance(app, FastAPI)

    return {
        "status": "ok",
        "title": getattr(app, "title"),
        "version": getattr(app, "version"),
    }
