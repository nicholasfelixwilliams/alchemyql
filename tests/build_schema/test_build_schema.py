from alchemyql import AlchemyQLSync, AlchemyQLAsync
from alchemyql.engine import AlchemyQL
import os
import pytest

from alchemyql.errors import ConfigurationError

from ..databases.a import A_Table
from ..databases.b import B_Table_1, B_Table_2, B_Table_3
from ..databases.c import C_Table


data_folder = os.path.join(os.path.dirname(__file__), "data")


def read_data_file(name: str) -> str:
    with open(os.path.join(data_folder, name), "r") as file:
        return file.read()


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
@pytest.mark.parametrize(
    "output_file,register_kwargs",
    [
        # No customisation
        ("A_test_case_plain.txt", {}),
        # Name customisation
        ("A_test_case_graphql_name.txt", {"graphql_name": "other_name"}),
        # Fields to include customisation
        (
            "A_test_case_include_fields.txt",
            {"include_fields": ["enum_field", "string_field"]},
        ),
        ("A_test_case_exclude_fields.txt", {"exclude_fields": ["enum_field"]}),
        (
            "A_test_case_include_exclude_fields.txt",
            {
                "include_fields": ["enum_field", "string_field"],
                "exclude_fields": ["enum_field"],
            },
        ),
        # Query/Filter customisation
        ("A_test_case_filter_fields.txt", {"filter_fields": ["string_field"]}),
        (
            "A_test_case_filter_fields2.txt",
            {
                "filter_fields": [
                    "string_field",
                    "int_field",
                    "float_field",
                    "bool_field",
                    "date_field",
                    "datetime_field",
                    "time_field",
                    "enum_field",
                ]
            },
        ),
        # Ordering customisation
        ("A_test_case_order_fields.txt", {"order_fields": ["string_field"]}),
        (
            "A_test_case_order_fields2.txt",
            {"order_fields": ["string_field", "int_field"]},
        ),
        # Pagination customisation
        ("A_test_case_pagination.txt", {"pagination": True}),
        (
            "A_test_case_pagination_default.txt",
            {"pagination": True, "default_limit": 1000},
        ),
        # Combination of everything
        (
            "A_test_case_combination.txt",
            {
                "exclude_fields": ["json_field", "bytes_field"],
                "filter_fields": ["string_field", "int_field"],
                "order_fields": ["string_field"],
                "pagination": True,
            },
        ),
    ],
)
def test_build_schema_a(cls: type[AlchemyQL], output_file: str, register_kwargs: dict):
    engine = cls()

    engine.register(A_Table, **register_kwargs)
    engine.build_schema()

    expected = read_data_file(output_file)

    assert engine.get_schema() == expected


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_build_schema_b(cls: type[AlchemyQL]):
    engine = cls()

    engine.register(
        B_Table_1,
        exclude_fields=["json_field"],
        filter_fields=["int_field"],
        pagination=True,
    )
    engine.register(
        B_Table_2,
        exclude_fields=["bytes_field"],
        filter_fields=["int_field", "string_field"],
        pagination=True,
        default_limit=5,
    )
    engine.register(
        B_Table_3,
        include_fields=["string_field"],
        filter_fields=["int_field", "string_field"],
    )
    engine.build_schema()

    expected = read_data_file("B.txt")

    assert engine.get_schema() == expected


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_build_schema_c(cls: type[AlchemyQL]):
    engine = cls()

    engine.register(
        C_Table,
        exclude_fields=["json_field", "bytes_field"],
        filter_fields=["string_field", "int_field"],
        order_fields=["string_field"],
        pagination=True,
    )
    engine.build_schema()

    expected = read_data_file("C.txt")

    assert engine.get_schema() == expected


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_invalid_column_ref(cls: type[AlchemyQL]):
    engine = cls()

    engine.register(A_Table, include_fields=["does-not-exist"])

    with pytest.raises(ConfigurationError):
        engine.build_schema()


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
@pytest.mark.parametrize("field", ["bytes_field", "json_field"])
def test_register_invalid_filter_column(cls: type[AlchemyQL], field: str):
    engine = cls()

    engine.register(A_Table, filter_fields=[field])

    with pytest.raises(ConfigurationError):
        engine.build_schema()


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_get_schema_before_built(cls: type[AlchemyQL]):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.get_schema()


def test_execute_query_before_schema_built_sync():
    engine = AlchemyQLSync()

    with pytest.raises(ConfigurationError):
        engine.execute_query("", None)  # type: ignore


async def test_execute_query_before_schema_built_async():
    engine = AlchemyQLAsync()

    with pytest.raises(ConfigurationError):
        await engine.execute_query("", None)  # type: ignore
