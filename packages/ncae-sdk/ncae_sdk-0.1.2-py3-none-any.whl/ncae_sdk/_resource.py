from typing import Annotated, Any, Optional, TypeVar, Union

from pydantic import BaseModel, BeforeValidator, ConfigDict, WrapSerializer, with_config
from pydantic_core import PydanticUndefined
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import Self, TypeAlias, TypedDict

T = TypeVar("T")

ResourceId = Union[int, str]
ResourceT = TypeVar("ResourceT", bound="Resource")


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        serialize_by_alias=True,
        validate_by_alias=False,
        validate_by_name=True,
    )

    def dump_api(self) -> dict[str, Any]:
        return self.model_dump(
            exclude_defaults=True,
            mode="json",
        )


class Resource(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        validate_by_alias=True,
        validate_by_name=True,
    )

    @classmethod
    def parse_api(cls, raw: Any) -> Self:
        return cls.model_validate(raw)


@with_config(
    extra="forbid",
    frozen=True,
    validate_by_alias=False,
    validate_by_name=True,
)
class ResourceDict(TypedDict):
    pass


def empty_str_to_none(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    return value


def none_to_empty_str(value: Optional[str], nxt: SerializerFunctionWrapHandler) -> str:
    result = nxt(value)
    return "" if result is None else result


def extract_nested_id(value: Any) -> Any:
    if isinstance(value, int) or isinstance(value, str):
        return value
    if isinstance(value, dict) and "id" in value:
        return value["id"]
    return PydanticUndefined


def serialize_nested_id(value: Any, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
    result = handler(value)
    return {"id": result}


OptionalStr: TypeAlias = Annotated[
    Optional[str],
    BeforeValidator(empty_str_to_none),
    WrapSerializer(none_to_empty_str),
]

NestedId: TypeAlias = Annotated[T, BeforeValidator(extract_nested_id), WrapSerializer(serialize_nested_id)]
ReadOnlyNestedId: TypeAlias = Annotated[T, BeforeValidator(extract_nested_id)]
