from typing import Generic, Optional

from typing_extensions import Protocol

from ncae_sdk.fastapi.extapi._contracts import CallbackT, CmdbT, ExtApiPhaseExtraVars


class ExtApiPhaseContextProtocol(Protocol, Generic[CmdbT, CallbackT]):
    @property
    def callback_data(self) -> CallbackT: ...

    @property
    def cmdb_data(self) -> CmdbT: ...

    @property
    def cmdb_data_previous(self) -> Optional[CmdbT]: ...

    @property
    def body(self) -> ExtApiPhaseExtraVars[CmdbT, CallbackT]: ...
