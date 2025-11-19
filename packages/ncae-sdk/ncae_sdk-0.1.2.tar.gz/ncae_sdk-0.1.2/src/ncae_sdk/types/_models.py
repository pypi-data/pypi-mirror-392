from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, computed_field


class Model(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )


class AuditLogChange(Model):
    field: str = Field(alias="field")
    old: str = Field(alias="old")
    new: str = Field(alias="new")


class InfluxDataPoint(Model):
    measurement: str = Field(alias="measurement")
    timestamp: Optional[datetime] = Field(alias="timestamp", default=None)
    field_data: dict[str, Union[str, int, float, bool]] = Field(alias="field_data")
    tag_data: dict[str, str] = Field(alias="tag_data", default_factory=dict)


class InfluxTagFilter(Model):
    key: str = Field(alias="key")
    value: str = Field(alias="value")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mode(self) -> str:
        return "exact"
