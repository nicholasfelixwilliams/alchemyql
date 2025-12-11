from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient

from alchemyql import AlchemyQLAsync, AlchemyQLSync
from alchemyql.engine import AlchemyQL
from alchemyql.fastapi.router import (
    create_alchemyql_router_async,
    create_alchemyql_router_sync,
)

from .databases.a import A_Table

schema = r'"type Query {\n  sample_tables: [sample_table]\n}\n\n\"\"\"SAMPLE_TABLE\"\"\"\ntype sample_table {\n  string_field: String!\n}"'

query = "query { sample_tables { string_field } }"

result = {
    "data": {
        "sample_tables": [
            {"string_field": "One"},
            {"string_field": "Two"},
            {"string_field": "Three"},
            {"string_field": "Four"},
            {"string_field": "Five"},
        ]
    },
    "errors": None,
}


def build_engine(cls: type[AlchemyQL]) -> AlchemyQL:
    engine = cls()
    engine.register(A_Table, include_fields=["string_field"])
    engine.build_schema()
    return engine


def db_sync_dependency(db):
    def _dep():
        yield db

    return _dep


@asynccontextmanager
async def get_db_async(session):
    """Yield the same async session for the request."""
    yield session


def test_sync_get_schema_sync():
    engine = build_engine(AlchemyQLSync)

    app = FastAPI()
    app.include_router(create_alchemyql_router_sync(engine, lambda: None))  # type: ignore
    client = TestClient(app)

    res = client.get("/graphql")

    assert res.status_code == 200
    assert res.text == schema


async def test_sync_get_schema_async():
    engine = build_engine(AlchemyQLAsync)

    app = FastAPI()
    app.include_router(create_alchemyql_router_async(engine, lambda: None))  # type: ignore
    client = TestClient(app)

    res = client.get("/graphql")

    assert res.status_code == 200
    assert res.text == schema


def test_sync_get_schema_sync_auth():
    engine = build_engine(AlchemyQLSync)

    app = FastAPI()
    app.include_router(create_alchemyql_router_sync(engine, lambda: None, lambda: True))  # type: ignore
    client = TestClient(app)

    res = client.get("/graphql")

    assert res.status_code == 200
    assert res.text == schema


async def test_sync_get_schema_async_auth():
    engine = build_engine(AlchemyQLAsync)

    app = FastAPI()
    app.include_router(
        create_alchemyql_router_async(engine, lambda: None, lambda: True)  # type: ignore
    )
    client = TestClient(app)

    res = client.get("/graphql")

    assert res.status_code == 200
    assert res.text == schema


def test_sync_execute_query_sync(db_sync):
    engine = build_engine(AlchemyQLSync)

    app = FastAPI()
    with db_sync("A") as db:
        app.include_router(create_alchemyql_router_sync(engine, lambda: db))  # type: ignore
        client = TestClient(app)

        res = client.post(
            "/graphql", json={"query": "query { sample_tables { string_field } }"}
        )

        assert res.status_code == 200
        assert res.json() == result


async def test_sync_execute_query_async(db_async):
    engine = build_engine(AlchemyQLAsync)

    async with db_async("A") as db:
        app = FastAPI()
        app.include_router(
            create_alchemyql_router_async(engine, lambda: db)  # type: ignore
        )
        client = TestClient(app)

        res = client.post("/graphql", json={"query": query})

        assert res.status_code == 200
        assert res.json() == result
