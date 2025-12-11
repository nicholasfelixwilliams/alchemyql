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

This provides you with the following 2 endpoints:

| Method | Url | Arguments | Description |
| ----- | ----- | ----- | ----- |
| GET | /graphql | None | Returns the GraphQL schema in SDL format | 
| POST | /graphql | Query (request body) | Executes the GraphQL query | 

## Variations

There are sync and async variations of this:

| Variation | Method | 
| ----- | ----- |
| Sync | create_alchemyql_router_sync |
| Async | create_alchemyql_router_async |

Both have the same arguments and function the same.

## Options

The following options are available as arguments to the create router methods:

| Argument | Type | Default | Description |
| ----- | ----- | ----- | ----- |
| engine | AlchemyQLSync or AlchemyQLAsync | - | (Mandatory) AlchemyQL engine  | 
| db_dependency | Callable | - | (Mandatory) Function to use for DB dependency | 
| auth_dependency | Callable | - | (Optional) Function to use for Auth dependency | 
| path | str | "/graphql" | URL path for the 2 endpoints | 
| tags | list[str] | ["GraphQL"] | OpenAPI tags for the endpoints | 