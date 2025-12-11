import json
import os
from contextlib import asynccontextmanager, contextmanager
from datetime import date, datetime, time
from pathlib import Path

import pytest
from sqlalchemy import StaticPool, create_engine, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .databases.a import Base as A_Base
from .databases.b import Base as B_Base
from .databases.d import Base as D_Base

TEST_DATABASES = {"A": A_Base, "B": B_Base, "D": D_Base}


def convert_values(row, model_cls):
    """
    Convert JSON strings into datetime/date/time Python objects.
    """
    converted = {}
    for key, val in row.items():
        col = getattr(model_cls, key).property.columns[0]
        pytype = col.type.python_type

        if pytype is datetime:
            converted[key] = datetime.fromisoformat(val)
        elif pytype is date:
            converted[key] = date.fromisoformat(val)
        elif pytype is time:
            converted[key] = time.fromisoformat(val)
        elif pytype is bytes:
            converted[key] = str(val).encode()
        else:
            converted[key] = val

    return converted


def populate_db_stmts(base, test_db: str):
    """
    Utility method to generate initial data population sql statements
    """
    stmts = []
    data = json.loads(
        Path(
            os.path.join(
                os.path.dirname(__file__), "databases", f"{test_db}.json".lower()
            )
        ).read_text()
    )

    table_name_to_class = {
        mapper.local_table.name: mapper.class_ for mapper in base.registry.mappers
    }

    for table_name, rows in data.items():
        model_cls = table_name_to_class.get(table_name)
        if not model_cls:
            raise ValueError(f"No mapped class found for table '{table_name}'")

        if rows:
            stmts.append(
                insert(model_cls).values(
                    [convert_values(row, model_cls) for row in rows]
                )
            )

    return stmts


@pytest.fixture
def db_sync():
    @contextmanager
    def _factory(db_name):
        engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        base = TEST_DATABASES[db_name]

        # Create DB tables
        base.metadata.create_all(engine)

        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        session = session_factory()

        for stmt in populate_db_stmts(base, db_name):
            session.execute(stmt)
        session.commit()

        try:
            yield session
        finally:
            session.close()

        # Cleanup test db
        base.metadata.drop_all(engine)

        engine.dispose()

    return _factory


@pytest.fixture
def db_async():
    @asynccontextmanager
    async def _factory(db_name):
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:", poolclass=StaticPool
        )
        base = TEST_DATABASES[db_name]

        # Create DB tables
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

        session_factory = sessionmaker(
            bind=engine,  # type: ignore
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with session_factory() as session:  # type: ignore
            for stmt in populate_db_stmts(base, db_name):
                await session.execute(stmt)
            await session.commit()

            try:
                yield session
            finally:
                await session.close()

        # Cleanup test db
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)

        await engine.dispose()

    return _factory
