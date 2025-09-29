"""YAML parsing utilities"""

from dataclasses import dataclass
from types import NoneType
from typing import Any, Generic, Type, TypeAlias, TypeVar

from cliyaml import regexp

T = TypeVar("T")


@dataclass
class Value(Generic[T]):
    value: T
    type: Type[T]
    comment: str | None = None


Tree: TypeAlias = dict[str, "Node"]
Node: TypeAlias = Value[int | float | str | bool | None | Tree]


def parse_value(s: str) -> tuple[Any, type]:
    """Parse a YAML value from the start of a string.

    For null values, a type when not null can be specified with a # (type) comment.

    Returns:
        (value, type)
    """

    val_type = NoneType

    if (substr := regexp.match(s, regexp.float)) is not None:
        value = float(substr)
        val_type = float

    elif (substr := regexp.match(s, regexp.int)) is not None:
        value = int(substr)
        val_type = int

    elif (substr := regexp.match(s, regexp.boolean)) is not None:
        value = substr == "true"
        val_type = bool

    elif (substr := regexp.match(s, regexp.string)) is not None:
        value = substr[1:-1]
        val_type = str

    else:
        substr = s.split("#")[0]
        value = substr.strip()
        if value == "":
            value = None
        else:
            val_type = str

    # Parse type hint from comment if value is null
    rest = s[len(substr) :].strip()
    if val_type is NoneType and rest.startswith("#"):
        if "int" in rest:
            val_type = int
        elif "float" in rest:
            val_type = float
        elif "str" in rest:
            val_type = str
        elif "bool" in rest:
            val_type = bool

    return (value, val_type)


def parse_lines(lines: list[str], indent=0, offset=0) -> tuple[Tree, int]:
    """Parse lines starting from the given offset, and at the given indentation level.

    If encountering higher indentation, parse the nested structure recursively.
    If encountering lower indentation, return the current data and offset for the caller to handle.
    """

    data: Tree = {}
    key = ""
    comments: list[str] = []

    while offset < len(lines):
        line_indent = (len(lines[offset]) - len(lines[offset].lstrip())) // 2
        line = lines[offset].strip()

        if line.startswith("#"):
            comments.append(line[1:].strip())
            offset += 1
            continue

        if line == "":
            comments = []
            offset += 1
            continue

        if line_indent == indent:
            key = line.split(":")[0].strip()
            value, type = parse_value(line[len(key) + 1 :].strip())
            data[key] = Value(value, type, "\n".join(comments))
            comments = []

        if line_indent > indent:
            child, offset = parse_lines(lines, line_indent, offset)
            data[key] = Value(child, dict, "\n".join(comments))
            comments = []

        if line_indent < indent:
            break

        offset += 1

    return data, offset


def to_dict(tree: Tree, prefix="") -> dict:
    """Convert a Tree to a flattened directory."""

    result = {}

    for key, node in tree.items():
        if isinstance(node.value, dict):
            d = to_dict(node.value, f"{prefix}{key}_")
            result |= d
        else:
            result[f"{prefix}{key}"] = node.value

    return result
