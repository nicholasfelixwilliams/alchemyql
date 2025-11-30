from datetime import date, datetime, time
from enum import Enum
from graphql import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLInputField,
    GraphQLInputType,
    GraphQLList,
)
from typing import cast

from .errors import ConfigurationError
from .scalars import (
    DateScalar,
    DateTimeScalar,
    TimeScalar,
    IntScalar,
    FloatScalar,
    BoolScalar,
    StringScalar,
)


IntFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="IntFilter",
        fields=lambda: {
            "eq": GraphQLInputField(IntScalar),
            "ne": GraphQLInputField(IntScalar),
            "gt": GraphQLInputField(IntScalar),
            "ge": GraphQLInputField(IntScalar),
            "lt": GraphQLInputField(IntScalar),
            "le": GraphQLInputField(IntScalar),
            "in": GraphQLInputField(GraphQLList(IntScalar)),
        },
    ),
)

FloatFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="FloatFilter",
        fields=lambda: {
            "eq": GraphQLInputField(FloatScalar),
            "ne": GraphQLInputField(FloatScalar),
            "gt": GraphQLInputField(FloatScalar),
            "ge": GraphQLInputField(FloatScalar),
            "lt": GraphQLInputField(FloatScalar),
            "le": GraphQLInputField(FloatScalar),
            "in": GraphQLInputField(GraphQLList(FloatScalar)),
        },
    ),
)

BoolFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="BoolFilter",
        fields=lambda: {
            "eq": GraphQLInputField(BoolScalar),
            "ne": GraphQLInputField(BoolScalar),
        },
    ),
)

StringFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="StringFilter",
        fields=lambda: {
            "eq": GraphQLInputField(StringScalar),
            "ne": GraphQLInputField(StringScalar),
            "contains": GraphQLInputField(StringScalar),
            "startswith": GraphQLInputField(StringScalar),
            "endswith": GraphQLInputField(StringScalar),
            "in": GraphQLInputField(GraphQLList(StringScalar)),
        },
    ),
)

DateTimeFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="DateTimeFilter",
        fields=lambda: {
            "eq": GraphQLInputField(DateTimeScalar),
            "ne": GraphQLInputField(DateTimeScalar),
            "gt": GraphQLInputField(DateTimeScalar),
            "ge": GraphQLInputField(DateTimeScalar),
            "lt": GraphQLInputField(DateTimeScalar),
            "le": GraphQLInputField(DateTimeScalar),
            "in": GraphQLInputField(GraphQLList(DateTimeScalar)),
        },
    ),
)

DateFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="DateFilter",
        fields=lambda: {
            "eq": GraphQLInputField(DateScalar),
            "ne": GraphQLInputField(DateScalar),
            "gt": GraphQLInputField(DateScalar),
            "ge": GraphQLInputField(DateScalar),
            "lt": GraphQLInputField(DateScalar),
            "le": GraphQLInputField(DateScalar),
            "in": GraphQLInputField(GraphQLList(DateScalar)),
        },
    ),
)

TimeFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="TimeFilter",
        fields=lambda: {
            "eq": GraphQLInputField(TimeScalar),
            "ne": GraphQLInputField(TimeScalar),
            "gt": GraphQLInputField(TimeScalar),
            "ge": GraphQLInputField(TimeScalar),
            "lt": GraphQLInputField(TimeScalar),
            "le": GraphQLInputField(TimeScalar),
            "in": GraphQLInputField(GraphQLList(TimeScalar)),
        },
    ),
)


def build_enum_filter(cls: GraphQLEnumType) -> GraphQLInputObjectType:
    return cast(
        GraphQLInputObjectType,
        GraphQLInputObjectType(
            name=f"{cls.name}_filter",
            fields=lambda: {
                "eq": GraphQLInputField(cls),
                "ne": GraphQLInputField(cls),
                "in": GraphQLInputField(GraphQLList(cls)),
            },
        ),
    )


def convert_to_filter(column, field: GraphQLInputType) -> GraphQLInputObjectType:
    py_type = column.type.python_type

    if py_type is int:
        return IntFilter
    elif py_type is str:
        return StringFilter
    elif py_type is bool:
        return BoolFilter
    elif py_type is float:
        return FloatFilter
    elif issubclass(py_type, Enum):
        return build_enum_filter(cast(GraphQLEnumType, field))
    elif py_type is datetime:
        return DateTimeFilter
    elif py_type is date:
        return DateFilter
    elif py_type is time:
        return TimeFilter
    raise ConfigurationError(
        "Filtering based on data types other than (int, str, bool, float, Enums, datetime, date, time) is not currently supported"
    )
