from typing import Final, Optional

from fastapi import Request
from typing_extensions import Generic, Self

from ncae_sdk._session import SessionContext
from ncae_sdk.fastapi._context import BaseContext
from ncae_sdk.fastapi._dependencies import AsyncNcaeClientDep, DependencyMixin, NcaeClientDep, ThreadPoolExecutorDep
from ncae_sdk.fastapi.extapi._context_async import AsyncExtApiPhaseContextMixin
from ncae_sdk.fastapi.extapi._context_sync import ExtApiPhaseContextMixin
from ncae_sdk.fastapi.extapi._contracts import (
    CallbackT,
    CmdbT,
    ExtApiDevice,
    ExtApiPhaseExtraVars,
    ExtApiPhaseRequest,
    ExtApiReportRequest,
    QueryT,
)
from ncae_sdk.fastapi.extapi._protocols import ExtApiPhaseContextProtocol
from ncae_sdk.fastapi.runner._parallel import ParallelRunner
from ncae_sdk.fastapi.runner._utils import ItemT


class ExtApiPhaseContext(
    ExtApiPhaseContextMixin[CmdbT, CallbackT],
    AsyncExtApiPhaseContextMixin[CmdbT, CallbackT],
    DependencyMixin,
    BaseContext,
    ExtApiPhaseContextProtocol[CmdbT, CallbackT],
    Generic[CmdbT, CallbackT],
):
    def __init__(
        self,
        body: ExtApiPhaseRequest[CmdbT, CallbackT],
        request: Request,
        ncae_client: NcaeClientDep,
        async_ncae_client: AsyncNcaeClientDep,
        thread_pool: ThreadPoolExecutorDep,
    ) -> None:
        self._body: Final[ExtApiPhaseRequest[CmdbT, CallbackT]] = body

        super().__init__(
            ncae_client=ncae_client,
            async_ncae_client=async_ncae_client,
            request=request,
            thread_pool=thread_pool,
        )

    @property
    def is_decommission(self) -> bool:
        return self._body.extra_vars.is_decommission

    @property
    def cmdb_data(self) -> CmdbT:
        return self._body.extra_vars.cmdb_data

    @property
    def cmdb_data_previous(self) -> Optional[CmdbT]:
        return self._body.extra_vars.cmdb_data_previous

    @property
    def callback_data(self) -> CallbackT:
        return self._body.extra_vars.callback_data

    @property
    def devices(self) -> list[ExtApiDevice]:
        return self._body.extra_vars.devices

    @property
    def body(self) -> ExtApiPhaseExtraVars[CmdbT, CallbackT]:
        return self._body.extra_vars

    def get_device_runner(self) -> ParallelRunner[Self, ExtApiDevice]:
        return self.get_parallel_runner(self._body.extra_vars.devices)

    def get_parallel_runner(self, items: list[ItemT]) -> ParallelRunner[Self, ItemT]:
        return ParallelRunner(
            ctx=self,
            items=items,
            hook_sync=self._publish_progress_update,
            hook_async=self._async_publish_progress_update,
        )

    def _build_session_context(self) -> SessionContext:
        return SessionContext(
            ncae_tenant_id=self._body.extra_vars.ncae_tenant_id,
            ncae_transaction_id=self._body.extra_vars.ncae_transaction_id,
        )


class ExtApiReportContext(DependencyMixin, BaseContext, Generic[QueryT]):
    def __init__(
        self,
        body: ExtApiReportRequest[QueryT],
        request: Request,
        ncae_client: NcaeClientDep,
        async_ncae_client: AsyncNcaeClientDep,
        thread_pool: ThreadPoolExecutorDep,
    ) -> None:
        self._body: Final[ExtApiReportRequest[QueryT]] = body

        super().__init__(
            ncae_client=ncae_client,
            async_ncae_client=async_ncae_client,
            request=request,
            thread_pool=thread_pool,
        )

    @property
    def body(self) -> ExtApiReportRequest[QueryT]:
        return self._body

    @property
    def devices(self) -> list[ExtApiDevice]:
        return self._body.devices

    @property
    def query(self) -> QueryT:
        return self._body.query
