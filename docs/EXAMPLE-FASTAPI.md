# FastAPI example usage

The following minimal example uses an async sqlalchemy connection.

```py
from alchemyql import AlchemyQLAsync
from fastapi import FastAPI
from pydantic import BaseModel

from .your_db import Table, get_db_session

app = FastAPI()

engine = AlchemyQLAsync()
engine.register(Table)
engine.build_schema()

class GraphQLRequest(BaseModel):
    query: str
    variables: dict[str, Any] | None = None

@app.post("/graphql/")
async def graphql(request: GraphQLRequest, db = Depends(get_db_session)):
    res = await engine.execute_query(
        request.query, variables=request.variables, db_session=db
    )

    response = {}
    if res.errors:
        response["errors"] = [str(err) for err in res.errors]
    if res.data:
        response["data"] = res.data

    return response

```