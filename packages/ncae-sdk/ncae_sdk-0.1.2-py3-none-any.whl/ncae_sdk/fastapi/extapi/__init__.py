from ncae_sdk.fastapi.extapi._context import ExtApiPhaseContext, ExtApiReportContext
from ncae_sdk.fastapi.extapi._contracts import (
    CallbackT,
    CmdbT,
    ExtApiCredential,
    ExtApiDevice,
    ExtApiDeviceModel,
    ExtApiPhaseExtraVars,
    ExtApiPhaseRequest,
    ExtApiReportField,
    ExtApiReportRequest,
    ExtApiReportResponse,
    QueryT,
)
from ncae_sdk.fastapi.extapi._decorators import extapi_phase_route, extapi_report_route

__all__ = [
    "CallbackT",
    "CmdbT",
    "ExtApiCredential",
    "ExtApiDevice",
    "ExtApiDeviceModel",
    "ExtApiPhaseContext",
    "ExtApiPhaseExtraVars",
    "ExtApiPhaseRequest",
    "ExtApiReportContext",
    "ExtApiReportField",
    "ExtApiReportRequest",
    "ExtApiReportResponse",
    "QueryT",
    "extapi_phase_route",
    "extapi_report_route",
]


__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "ncae_sdk.fastapi.extapi")
