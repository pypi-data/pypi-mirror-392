from typing import Annotated, Any, List, Optional

from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema, WrapSerializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler
from typing_extensions import TypeAlias


def empty_str_to_none(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    return value


def none_to_empty_str(value: Optional[str], nxt: SerializerFunctionWrapHandler) -> str:
    result = nxt(value)
    return "" if result is None else result


def _parse_cmdb_text_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return value.strip().splitlines()

    raise ValueError(f"Expected a string or list of strings, got {type(value)}")


def _serialize_cmdb_text_list(value: list[str]) -> str:
    return "\n".join(value)


CmdbTextList: TypeAlias = Annotated[
    List[str],
    BeforeValidator(_parse_cmdb_text_list),
    PlainSerializer(_serialize_cmdb_text_list),
    WithJsonSchema({"type": "string"}, mode="validation"),
]
CmdbTextList.__doc__ = """
Custom Pydantic field type for handling CMDB fields of type `TextListInput`.
This will always return a list of strings, one per each line in the input field.
While empty lines are not filtered out, a fully empty field will return an empty list.

:type: list[str]
"""

CmdbOptionalStr: TypeAlias = Annotated[
    Optional[str],
    BeforeValidator(empty_str_to_none),
    WrapSerializer(none_to_empty_str),
]
CmdbOptionalStr.__doc__ = """
Custom Pydantic field type for handling optional strings, e.g. any CMDB field of type `TextInput`.
When receiving a value from NCAE Core, it will convert empty strings to `None`.
When sending a value to NCAE Core, it will convert `None` back to an empty string.

:type: Optional[str]
"""
