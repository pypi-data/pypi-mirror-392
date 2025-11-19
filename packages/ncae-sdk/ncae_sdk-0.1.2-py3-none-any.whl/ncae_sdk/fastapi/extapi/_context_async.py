import socket
from typing import Any, Generic, Optional

from ncae_sdk.fastapi._context import BaseContext
from ncae_sdk.fastapi.extapi._contracts import CallbackT, CmdbT
from ncae_sdk.fastapi.extapi._protocols import ExtApiPhaseContextProtocol
from ncae_sdk.fastapi.runner._progress import ProgressUpdate
from ncae_sdk.types import LogLevel, PhaseStatus


class AsyncExtApiPhaseContextMixin(
    BaseContext, ExtApiPhaseContextProtocol[CmdbT, CallbackT], Generic[CmdbT, CallbackT]
):
    async def async_log_debug(
        self, message: str, *args: Any, title: Optional[str] = None, hostname: Optional[str] = None
    ) -> None:
        await self.async_log(LogLevel.DEBUG, message, *args, title=title, hostname=hostname)

    async def async_log_info(
        self, message: str, *args: Any, title: Optional[str] = None, hostname: Optional[str] = None
    ) -> None:
        await self.async_log(LogLevel.INFORMATIONAL, message, *args, title=title, hostname=hostname)

    async def async_log_warning(
        self, message: str, *args: Any, title: Optional[str] = None, hostname: Optional[str] = None
    ) -> None:
        await self.async_log(LogLevel.WARNING, message, *args, title=title, hostname=hostname)

    async def async_log_error(
        self, message: str, *args: Any, title: Optional[str] = None, hostname: Optional[str] = None
    ) -> None:
        await self.async_log(LogLevel.ERROR, message, *args, title=title, hostname=hostname)

    async def async_log(
        self,
        level: LogLevel,
        message: str,
        *args: Any,
        title: Optional[str] = None,
        hostname: Optional[str] = None,
    ) -> None:
        message = (message % args) if args else message
        title = title or self._request.app.title
        hostname = hostname or socket.gethostname()

        self.internal_logger.log(
            level.to_native(),
            "Publishing service [%(hostname)s] %(title)s: %(message)s",
            {"title": title, "hostname": hostname, "message": message},
        )

        await self.async_client.service_instance_logs.create(
            status=level,
            hostname=hostname or socket.gethostname(),
            title=title,
            text=message,
            service_instance_id=self.body.ncae_service_instance_id,
        )

    async def async_get_phase_status(self) -> PhaseStatus:
        phase = await self.async_client.phase_instances.get(self.body.ncae_phase_instance_id)
        assert phase is not None, "Could not retrieve own phase instance"

        return phase.status

    async def async_update_phase_status(self, status: PhaseStatus) -> None:
        await self.async_client.phase_instances.update(self.body.ncae_phase_instance_id, status=status)

    async def async_update_callback_data(self) -> None:
        callback_data = self.callback_data.model_dump(mode="json")
        await self.async_client.cmdb_entries.update(
            self.body.ncae_cmdb_entry_id,
            callback_data=callback_data,
        )

    async def _async_publish_progress_update(self, update: ProgressUpdate) -> None:
        await self.async_log_info(
            "Processed %d out of %d items in %.2f seconds (%.2f%%)",
            update.current,
            update.total,
            update.elapsed_time.total_seconds(),
            update.percentage,
            title=f"Progress Update ({update.percentage:.2f}%)",
        )
