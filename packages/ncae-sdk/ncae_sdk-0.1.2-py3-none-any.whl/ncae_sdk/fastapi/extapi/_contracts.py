from typing import Any, Generic, Optional, Union

from pydantic import BaseModel, Field, GetJsonSchemaHandler, model_validator
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from typing_extensions import Self, TypeAlias, TypedDict, TypeVar

from ncae_sdk.fastapi._context import BaseRequestModel, BaseResponseModel, EmptyModel
from ncae_sdk.fastapi._utils import extract_pydantic_model_keys

CmdbT = TypeVar("CmdbT", bound=BaseModel, default=EmptyModel)
CallbackT = TypeVar("CallbackT", bound=BaseModel, default=EmptyModel)
QueryT = TypeVar("QueryT", bound=BaseModel, default=EmptyModel)

ExtApiReportResponseT = TypeVar("ExtApiReportResponseT", bound=BaseModel)


class ExtApiCredential(BaseRequestModel):
    name: str = Field(alias="name")
    username: str = Field(alias="username")
    password: str = Field(alias="password")
    become_password: str = Field(alias="become_password")


class ExtApiDeviceModel(BaseRequestModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name")
    slug: str = Field(alias="slug")


class ExtApiDevice(BaseRequestModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name")
    host: str = Field(alias="ip")
    verify_tls: bool = Field(alias="verify_tls")
    group_ids: list[int] = Field(alias="device_groups")
    target_names: list[str] = Field(alias="device_targets", default_factory=list)
    extra_vars: dict[str, Any] = Field(alias="extra_vars")
    device_model: ExtApiDeviceModel = Field(alias="device_model")
    credential: Optional[ExtApiCredential] = Field(alias="credential", default=None, validate_default=True)


class ExtApiPhaseExtraVars(BaseRequestModel, Generic[CmdbT, CallbackT]):
    is_decommission: bool = Field(alias="decommission")
    cmdb_data: CmdbT = Field(alias="data")
    cmdb_data_previous: Optional[CmdbT] = Field(alias="old_data", default=None)
    callback_data: CallbackT = Field(alias="callback_data", frozen=False)
    devices: list[ExtApiDevice] = Field(alias="devices")

    ncae_base_url: str = Field(alias="ncae_base_url")
    ncae_service_id: int = Field(alias="service_id")
    ncae_service_instance_id: int = Field(alias="service_instance_id")
    ncae_phase_instance_id: int = Field(alias="phase_instance_id")
    ncae_cmdb_entry_id: int = Field(alias="ncae_cmdb_entry_id")
    ncae_tenant_id: int = Field(alias="ncae_tenant_id")
    ncae_tenant_slug: str = Field(alias="ncae_tenant_slug")
    ncae_transaction_id: str = Field(alias="transaction_id")

    @model_validator(mode="before")
    @classmethod
    def inject_defaults(cls, data: Any) -> Any:
        # Due to `callback_data` being a generic, there is no easy way to inject an "empty" default value.
        # Therefore, this model validator ensures that at least an empty dict is provided if none was given.
        # Additionally, any non-dict value is forced to be an empty dict, as old NCAE Core versions might send `null`.
        if isinstance(data, dict):
            if not isinstance(data.get("callback_data"), dict):
                data["callback_data"] = {}

        return data


class ExtApiPhaseRequest(BaseRequestModel, Generic[CmdbT, CallbackT]):
    limit: Optional[str] = Field(alias="limit", default=None)
    extra_vars: ExtApiPhaseExtraVars[CmdbT, CallbackT] = Field(alias="extra_vars")


class ExtApiReportRequest(BaseRequestModel, Generic[QueryT]):
    devices: list[ExtApiDevice] = Field(alias="devices", default_factory=list)
    ncae_tenant_id: int = Field(alias="tenant")

    # Technically, all custom fields provided by a template are provided as top-level values.
    # To still provide some structure, these are hereby grouped under `query`, with the user-specified model.
    query: QueryT = Field(alias="query")

    # When an OTR is associated with a single device, its data will be provided top-level here.
    # The modern alternative is to use device / device groups targeting instead, stored in `devices`.
    device_host: Optional[str] = Field(alias="ip", default=None)
    device_verify_tls: Optional[bool] = Field(alias="verify_tls", default=None)
    device_username: Optional[str] = Field(alias="username", default=None)
    device_password: Optional[str] = Field(alias="password", default=None)
    device_become_password: Optional[str] = Field(alias="become_password", default=None)

    @model_validator(mode="before")
    @classmethod
    def validate_top_level_query(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(values, dict):
            return values

        # Extract all keys that do not belong to this model, respecting potential aliases
        own_keys = extract_pydantic_model_keys(cls)
        extra_keys = set(values.keys()).difference(own_keys)

        # Move all these extra keys under `query` to parse with the user-provided model
        query_data: dict[str, Any] = {}
        for extra_key in extra_keys:
            query_data[extra_key] = values.pop(extra_key)
        values["query"] = query_data

        return values

    @model_validator(mode="after")
    def validate_static_device(self) -> Self:
        base_fields = [self.device_host, self.device_verify_tls]
        credential_fields = [self.device_username, self.device_password, self.device_become_password]

        if any(f is not None for f in base_fields + credential_fields) and not all(f is not None for f in base_fields):
            raise ValueError("If any device field is provided, all base fields must be provided")

        if any(f is not None for f in credential_fields) and not all(f is not None for f in credential_fields):
            raise ValueError("If any device credential field is provided, all credential fields must be provided")

        return self

    @model_validator(mode="after")
    def validate_query_model(self) -> Self:
        own_fields = extract_pydantic_model_keys(self.__class__)
        query_fields = extract_pydantic_model_keys(self.query.__class__)
        overlapping_fields = own_fields.intersection(query_fields)

        if overlapping_fields:
            raise ValueError(f"Query model fields overlap with request fields: {', '.join(overlapping_fields)}")

        return self

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler, /) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema = handler.resolve_ref_schema(schema)
        assert schema.get("type") == "object" and isinstance(schema.get("properties"), dict)

        query_schema = schema["properties"].pop("query")
        query_schema = handler.resolve_ref_schema(query_schema)
        assert query_schema.get("type") == "object" and isinstance(query_schema.get("properties"), dict)

        schema["properties"].update(query_schema["properties"])
        return schema


ExtApiReportFieldValue: TypeAlias = Union[str, int, float, bool, None]


class ExtApiReportLinkField(TypedDict):
    value: ExtApiReportFieldValue
    href: str


class ExtApiReportHtmlField(TypedDict):
    value: ExtApiReportFieldValue
    extension: str


ExtApiReportField: TypeAlias = Union[
    ExtApiReportFieldValue,
    ExtApiReportLinkField,
    ExtApiReportHtmlField,
]


class ExtApiReportResponse(BaseResponseModel):
    field_names: list[str] = Field(serialization_alias="fields")
    field_data: list[dict[str, ExtApiReportField]] = Field(serialization_alias="field_data")
