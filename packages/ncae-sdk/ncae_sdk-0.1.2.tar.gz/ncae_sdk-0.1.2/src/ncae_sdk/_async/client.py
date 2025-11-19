import os
from functools import cached_property
from types import TracebackType
from typing import Optional, Type

from httpx import AsyncBaseTransport
from typing_extensions import Self

from ncae_sdk._async.session import AsyncSession
from ncae_sdk._auth import Auth, SessionAuth
from ncae_sdk._session import SessionContext
from ncae_sdk._util import parse_env_bool, parse_env_int
from ncae_sdk.endpoints import (
    AsyncAuditLogEndpoint,
    AsyncAwxModuleEndpoint,
    AsyncChangeScheduleEndpoint,
    AsyncChangeScheduleRunEndpoint,
    AsyncCmdbEntryEndpoint,
    AsyncCredentialEndpoint,
    AsyncDeviceEndpoint,
    AsyncDeviceGroupEndpoint,
    AsyncDeviceModelEndpoint,
    AsyncExtApiAuthEndpoint,
    AsyncExtApiServiceEndpoint,
    AsyncGrafanaDashboardEndpoint,
    AsyncGrafanaSystemEndpoint,
    AsyncInfluxRepositoryEndpoint,
    AsyncInfluxSystemEndpoint,
    AsyncModuleEndpoint,
    AsyncPhaseEndpoint,
    AsyncPhaseInstanceEndpoint,
    AsyncServiceEndpoint,
    AsyncServiceInstanceEndpoint,
    AsyncServiceInstanceLogEndpoint,
    AsyncSharedDataBucketEndpoint,
    AsyncSharedDataSubscriberEndpoint,
    AsyncTagEndpoint,
    AsyncTagRelationEndpoint,
    AsyncTenantEndpoint,
    AsyncTransactionEndpoint,
    AsyncUploadFileEndpoint,
    AsyncUsageLogEndpoint,
    AsyncUserEndpoint,
)
from ncae_sdk.endpoints._async.favourite import AsyncFavouriteEndpoint
from ncae_sdk.endpoints._async.report import AsyncReportEndpoint


class AsyncClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        auth: Optional[Auth] = None,
        timeout: Optional[int] = None,
        verify: Optional[bool] = None,
        httpx_transport: Optional[AsyncBaseTransport] = None,
    ) -> None:
        """
        Initializes a new asynchronous client for interacting with the NCAE API.

        This client provides access to various endpoints such as audit logs, devices, credentials, and more. It is
        based on an underlying session that uses httpx for asynchronous HTTP requests. For these reasons, it is
        recommended to use this client as a context manager, as this ensures cleanup and allows proper pooling.

        All arguments are marked as optional, which will fallback to environment variables or default values.
        If no suitable configuration is found, an error will be raised during instantiation.

        :param base_url: The base URL of the NCAE API, e.g. `https://ncae.example.com/api/`.
        :param auth: An instance of :class:`Auth` that provides authentication for the API requests.
        :param timeout: The desired timeout for API requests in seconds. Usage of default value is recommended.
        :param verify: Whether to verify SSL certificates. Set to `False` if you are using a self-signed certificate.
        """
        if not base_url:
            base_url = os.environ.get("NCAE_SDK_BASE_URL")
            if not base_url:
                raise ValueError("Unable to determine NCAE SDK base URL.")

        if not auth:
            username = os.environ.get("NCAE_SDK_USERNAME")
            password = os.environ.get("NCAE_SDK_PASSWORD")
            if not username or not password:
                raise ValueError("Unable to determine NCAE SDK authentication credentials.")

            auth = SessionAuth(username=username, password=password)

        if timeout is None:
            if value := os.environ.get("NCAE_SDK_HTTP_TIMEOUT"):
                timeout = parse_env_int(value)
            else:
                timeout = 5

        if verify is None:
            if value := os.environ.get("NCAE_SDK_HTTP_VERIFY"):
                verify = parse_env_bool(value)
            else:
                verify = True

        self._session: AsyncSession = AsyncSession.create(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            verify=verify,
            httpx_transport=httpx_transport,
        )

    def clone_with_context(self, context: SessionContext) -> Self:
        instance = self.__class__.__new__(self.__class__)
        instance._session = self._session.clone(context)
        return instance

    async def close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def ping(self) -> None:
        await self._session.get("readyz")

    @property
    def session(self) -> AsyncSession:
        return self._session

    @cached_property
    def audit_logs(self) -> AsyncAuditLogEndpoint:
        return AsyncAuditLogEndpoint(session=self._session)

    @cached_property
    def awx_modules(self) -> AsyncAwxModuleEndpoint:
        return AsyncAwxModuleEndpoint(session=self._session)

    @cached_property
    def change_schedules(self) -> AsyncChangeScheduleEndpoint:
        return AsyncChangeScheduleEndpoint(session=self._session)

    @cached_property
    def change_schedule_runs(self) -> AsyncChangeScheduleRunEndpoint:
        return AsyncChangeScheduleRunEndpoint(session=self._session)

    @cached_property
    def cmdb_entries(self) -> AsyncCmdbEntryEndpoint:
        return AsyncCmdbEntryEndpoint(session=self._session)

    @cached_property
    def credentials(self) -> AsyncCredentialEndpoint:
        return AsyncCredentialEndpoint(session=self._session)

    @cached_property
    def devices(self) -> AsyncDeviceEndpoint:
        return AsyncDeviceEndpoint(session=self._session)

    @cached_property
    def device_groups(self) -> AsyncDeviceGroupEndpoint:
        return AsyncDeviceGroupEndpoint(session=self._session)

    @cached_property
    def device_models(self) -> AsyncDeviceModelEndpoint:
        return AsyncDeviceModelEndpoint(session=self._session)

    @cached_property
    def ext_api_auths(self) -> AsyncExtApiAuthEndpoint:
        return AsyncExtApiAuthEndpoint(session=self._session)

    @cached_property
    def ext_api_services(self) -> AsyncExtApiServiceEndpoint:
        return AsyncExtApiServiceEndpoint(session=self._session)

    @cached_property
    def favourites(self) -> AsyncFavouriteEndpoint:
        return AsyncFavouriteEndpoint(session=self._session)

    @cached_property
    def grafana_dashboards(self) -> AsyncGrafanaDashboardEndpoint:
        return AsyncGrafanaDashboardEndpoint(session=self._session)

    @cached_property
    def grafana_systems(self) -> AsyncGrafanaSystemEndpoint:  # noqa: F821
        return AsyncGrafanaSystemEndpoint(session=self._session)

    @cached_property
    def influx_repositories(self) -> AsyncInfluxRepositoryEndpoint:
        return AsyncInfluxRepositoryEndpoint(session=self._session)

    @cached_property
    def influx_systems(self) -> AsyncInfluxSystemEndpoint:
        return AsyncInfluxSystemEndpoint(session=self._session)

    @cached_property
    def modules(self) -> AsyncModuleEndpoint:
        return AsyncModuleEndpoint(session=self._session)

    @cached_property
    def phases(self) -> AsyncPhaseEndpoint:
        return AsyncPhaseEndpoint(session=self._session)

    @cached_property
    def phase_instances(self) -> AsyncPhaseInstanceEndpoint:
        return AsyncPhaseInstanceEndpoint(session=self._session)

    @cached_property
    def reports(self) -> AsyncReportEndpoint:
        return AsyncReportEndpoint(session=self._session)

    @cached_property
    def services(self) -> AsyncServiceEndpoint:
        return AsyncServiceEndpoint(session=self._session)

    @cached_property
    def service_instances(self) -> AsyncServiceInstanceEndpoint:
        return AsyncServiceInstanceEndpoint(session=self._session)

    @cached_property
    def service_instance_logs(self) -> AsyncServiceInstanceLogEndpoint:
        return AsyncServiceInstanceLogEndpoint(session=self._session)

    @cached_property
    def shared_data_buckets(self) -> AsyncSharedDataBucketEndpoint:
        return AsyncSharedDataBucketEndpoint(session=self._session)

    @cached_property
    def shared_data_subscribers(self) -> AsyncSharedDataSubscriberEndpoint:
        return AsyncSharedDataSubscriberEndpoint(session=self._session)

    @cached_property
    def tags(self) -> AsyncTagEndpoint:
        return AsyncTagEndpoint(session=self._session)

    @cached_property
    def tag_relations(self) -> AsyncTagRelationEndpoint:
        return AsyncTagRelationEndpoint(session=self._session)

    @cached_property
    def tenants(self) -> AsyncTenantEndpoint:
        return AsyncTenantEndpoint(session=self._session)

    @cached_property
    def transactions(self) -> AsyncTransactionEndpoint:
        return AsyncTransactionEndpoint(session=self._session)

    @cached_property
    def upload_files(self) -> AsyncUploadFileEndpoint:
        return AsyncUploadFileEndpoint(session=self._session)

    @cached_property
    def usage_logs(self) -> AsyncUsageLogEndpoint:
        return AsyncUsageLogEndpoint(session=self._session)

    @cached_property
    def users(self) -> AsyncUserEndpoint:
        return AsyncUserEndpoint(session=self._session)
