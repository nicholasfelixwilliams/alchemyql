<p>
  <img src="./docs/logo.png" width="180" style="padding: 10px" align="left" />
  <strong style="font-size: 3em">Alchemy QL</strong><br>
  <em>Lightweight GraphQL engine powered by SQLAlchemy</em>
</p>

---

### 🚀 Key Features
Alchemy QL's key features include:

- **Read Only** - Provides read-only graphql interface into your database 
- **Data Type Support** - Currently supported data types:
    - Built in types: int, float, bool, str, bytes
    - Date types: date, datetime, time
    - Enums
    - JSON fields
- **Query Options** - Currently supported query options:
    - Filtering 
    - Ordering
    - Pagination (using offset & limit)
- **Sync & Async support** 
- **Optimised SQL Queries** 

---

### 📦 Dependencies

- SQLAlchemy 2
- Graph QL core

---

### 📘 How to use

**Step 1** - Create your Alchemy QL engine (sync or async):

```py
from alchemyql import AlchemyQLSync, AlchemyQLAsync

sync_engine = AlchemyQLSync()
async_engine = AlchemyQLSync()
```

**Step 2** - Register your sqlalchemy tables:

```py
from your_db import Table

engine.register(
    Table, 
    include_fields=["field_one", "field_two"],
    filter_fields=["field_one"],
    order_fields=["field_one"],
    pagination=True,
    max_limit=100
    ...
)
```


**Step 3** - Build your schema:

```py
engine.build_schema()
```

**Step 4** - Run queries:

```py
query = "query { table { field } }"
db = session_factory() # SQLAlchemy DB session

# Sync Variation
res = sync_engine.execute_query(query=query, db_session=db)

# Async Variation
res = await async_engine.execute_query(query=query, db_session=db)
```

---

### 📘 Supported Options

**Registering Table:**

| Key   | Type  | Default | Description |
| ----- | ----- | ----- | ----- |
| graphql_name | str | None | Customise the graphql type name (defaults to sql tablename) | 
| description | str | None | Customise the graphql type descripton | 
| include_fields | list[str] | None | Allow only specific fields to be exposed | 
| exclude_fields | list[str] | [] | Block specific fields from being exposed | 
| filter_fields | list[str] | [] | Allow filtering for specific fields | 
| order_fields | list[str] | [] | Allow ordering for specific fields | 
| default_order | dict[str, Order] | None | Default order to apply to queries | 
| pagination | bool | False | Whether to support pagination | 
| default_limit | int | None | Default number of records that can be returned in 1 query | 
| max_limit | int | None | Maximum number of records that can be returned in 1 query | 

**NOTE:** if you do not specify include_fields or exclude_fields it will default expose all fields.

**Filtering Options:**

| Type | Supported Filters |
| ----- | ----- |
| int | eq, ne, gt, ge, lt, le, in |
| float | eq, ne, gt, ge, lt, le, in |
| bool | eq, ne |
| str | eq, ne, contains, startswith, endswith, in |
| date | eq, ne, gt, ge, lt, le, in |
| datetime | eq, ne, gt, ge, lt, le, in |
| time | eq, ne, gt, ge, lt, le, in |
| Enum | eq, ne, in |

All other types are not currently supported for filtering.

---

### Logging

AlchemyQL uses the "alchemyql" logger.

---

### License

This project is licensed under the terms of the MIT license.