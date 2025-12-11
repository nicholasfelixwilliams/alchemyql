# FastAPI example usage

The following minimal example uses an async sqlalchemy connection.

```py
from alchemyql import AlchemyQLAsync
from alchemyql.fastapi import create_alchemyql_router_async
from fastapi import FastAPI
from .your_db import Table, get_db_session

app = FastAPI()

engine = AlchemyQLAsync()
engine.register(Table)
engine.build_schema()

app.include_router(create_alchemyql_router_async(engine, get_db_session))

```