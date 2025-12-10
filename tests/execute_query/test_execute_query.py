import json
from pathlib import Path
from typing import TypeVar

import pytest

from alchemyql import AlchemyQLAsync, AlchemyQLSync
from alchemyql.engine import AlchemyQL
from alchemyql.models import Order

from ..databases.a import A_Table
from ..databases.b import B_Table_1, B_Table_2, B_Table_3
from ..databases.d import D_Table_1, D_Table_2, D_Table_3


def load_test_cases():
    path = Path(__file__).parent / "data"
    test_cases = []
    for file in path.rglob("*.json"):
        with open(file, "r") as f:
            test_case = json.load(f)
            test_case["id"] = str(file.relative_to(path))
            test_case["db"] = file.parent.name
            test_cases.append(test_case)
    return test_cases


T = TypeVar("T", bound=AlchemyQL)


def build_ql_engine(engine_cls: type[T], db: str) -> T:
    engine = engine_cls()

    match db:
        case "A":
            fields = [
                "string_field",
                "int_field",
                "float_field",
                "bool_field",
                "date_field",
                "datetime_field",
                "time_field",
                "enum_field",
            ]
            engine.register(
                A_Table,
                filter_fields=fields,
                order_fields=fields,
                default_order={"int_field": Order.ASC},
                pagination=True,
                max_limit=100,
            )
        case "B":
            fields = [
                "string_field",
                "int_field",
                "float_field",
                "bool_field",
                "date_field",
                "datetime_field",
                "time_field",
                "enum_field",
            ]
            params = {
                "filter_fields": fields,
                "order_fields": fields,
                "default_order": {"int_field": Order.ASC},
                "pagination": True,
            }
            engine.register(B_Table_1, **params)
            engine.register(B_Table_2, **params)
            engine.register(B_Table_3, **params)
        case "D":
            engine.register(
                D_Table_1,
                include_fields=["int_field", "string_field"],
                relationships=["t2_rel", "t3_rel"],
                order_fields=["int_field"],
                pagination=True,
            )
            engine.register(
                D_Table_2,
                include_fields=["int_field", "string_field"],
                relationships=["t1_rel", "t3_rel"],
                order_fields=["int_field"],
                pagination=True,
            )
            engine.register(
                D_Table_3,
                include_fields=["int_field", "string_field"],
                relationships=["t1_rel", "t2_rel"],
                order_fields=["int_field"],
                pagination=True,
            )

    engine.build_schema()
    return engine


@pytest.mark.parametrize("test_case", load_test_cases(), ids=lambda x: x["id"])
def test_sync_queries(db_sync, test_case):
    engine: AlchemyQLSync = build_ql_engine(AlchemyQLSync, test_case["db"])
    with db_sync(test_case["db"]) as db:
        res = engine.execute_query(
            query=test_case["query"], variables=test_case["variables"], db_session=db
        )

        assert res.errors is None
        assert res.data == test_case["expected"]


@pytest.mark.parametrize("test_case", load_test_cases(), ids=lambda x: x["id"])
async def test_async_queries(db_async, test_case):
    engine: AlchemyQLAsync = build_ql_engine(AlchemyQLAsync, test_case["db"])
    async with db_async(test_case["db"]) as db:
        res = await engine.execute_query(
            query=test_case["query"], variables=test_case["variables"], db_session=db
        )

        assert res.errors is None
        assert res.data == test_case["expected"]


"""
Invalid queries - we expect these to error

All queries are for test database A
"""
invalid_queries = [
    "query { does_not_exist { int_field } }",
    "query { sample_tables { } }query { sample_tables { does_not_exist } }",
    "query { sample_tables { does_not_exist int_field } }",
    "query { sample_tables (filter: {int_field: {dne: 1}}) { int_field } }",
    "query { sample_tables (filter: {does_not_exist: {eq: 1}}) { int_field } }",
    "query { sample_tables (order: {int_field: DNE}) { int_field } }",
    "query { sample_tables (limit: -1) { int_field } }",
    "query { sample_tables (limit: 2000) { int_field } }",
    "query { sample_tables (offset: -1) { int_field } }",
    "query { sample_tables (filter: {int_field: {gt: $var}}) { int_field } }",
]


@pytest.mark.parametrize("query", invalid_queries)
def test_sync_invalid_queries(db_sync, query):
    engine: AlchemyQLSync = build_ql_engine(AlchemyQLSync, "A")
    with db_sync("A") as db:
        res = engine.execute_query(query=query, variables=None, db_session=db)

        assert res.errors is not None


@pytest.mark.parametrize("query", invalid_queries)
async def test_async_invalid_queries(db_async, query):
    engine: AlchemyQLAsync = build_ql_engine(AlchemyQLAsync, "A")
    async with db_async("A") as db:
        res = await engine.execute_query(query=query, variables=None, db_session=db)

        assert res.errors is not None


def test_query_depth_exceeded_sync(db_sync):
    engine = AlchemyQLSync(max_query_depth=2)
    engine.register(D_Table_1, relationships=["t2_rel"])
    engine.register(
        D_Table_2,
        relationships=["t1_rel"],
    )
    engine.build_schema()

    query = "query { sample_table_1s { t2_rel { t1_rel { t2_rel { int_field } } } } }"

    with db_sync("D") as db:
        res = engine.execute_query(query=query, variables=None, db_session=db)

        assert res.errors is not None


async def test_query_depth_exceeded_async(db_async):
    engine = AlchemyQLAsync(max_query_depth=2)
    engine.register(D_Table_1, relationships=["t2_rel"])
    engine.register(
        D_Table_2,
        relationships=["t1_rel"],
    )
    engine.build_schema()

    query = "query { sample_table_1s { t2_rel { t1_rel { t2_rel { int_field } } } } }"

    async with db_async("D") as db:
        res = await engine.execute_query(query=query, variables=None, db_session=db)

        assert res.errors is not None
