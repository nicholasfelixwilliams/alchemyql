from enum import Enum
from sqlalchemy import select, desc, Select
from sqlalchemy.engine.row import RowMapping
from typing import Any

from .errors import QueryExecutionError
from .models import Table


def convert_enums(obj):
    """Recursively convert Enum objects inside dict/list/tuple/RowMapping."""

    # Enum → convert to string (name)
    if isinstance(obj, Enum):
        return obj.name

    # Dict/list, convert all
    elif isinstance(obj, (dict, RowMapping)):
        return {key: convert_enums(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(convert_enums(item) for item in obj)
    return obj


def build_sql_select_stmt(
    table,
    columns: list[str],
    filters: dict[str, Any] | None = None,
    offset: int | None = None,
    limit: int | None = None,
    order: dict[str, Any] | None = None,
) -> Select:
    """
    Build a SQLAlchemy Select statement based on GraphQL args.
    """
    # Step 1 - Build SELECT & FROM clauses
    cols = [getattr(table, col) for col in columns]
    stmt = select(*cols)

    # Step 2 - Build WHERE clause
    if filters:
        for col_name, operations in filters.items():
            column = getattr(table, col_name)
            for op, val in operations.items():
                if op == "eq":
                    stmt = stmt.where(column == val)
                elif op == "ne":
                    stmt = stmt.where(column != val)
                elif op == "lt":
                    stmt = stmt.where(column < val)
                elif op == "le":
                    stmt = stmt.where(column <= val)
                elif op == "gt":
                    stmt = stmt.where(column > val)
                elif op == "ge":
                    stmt = stmt.where(column >= val)
                elif op == "contains":
                    stmt = stmt.where(column.contains(val))
                elif op == "in":
                    stmt = stmt.where(column.in_(val))
                elif op == "startswith":
                    stmt = stmt.where(column.startswith(val))
                elif op == "endswith":
                    stmt = stmt.where(column.endswith(val))

    # Step 3 - Build pagination clauses (OFFSET, LIMIT)
    if offset is not None:
        stmt = stmt.offset(offset)

    if limit is not None:
        stmt = stmt.limit(limit)

    # Step 4 - Build ORDER BY clause
    if order:
        for col_name, direction in order.items():
            column = getattr(table, col_name)
            if str(direction).upper() == "DESC":
                column = desc(column)
            stmt = stmt.order_by(column)
    return stmt


def validations(table: Table, **kwargs):
    # Validate limit
    if limit := kwargs.get("limit"):
        if limit < 1 or (table.max_limit and limit > table.max_limit):
            raise QueryExecutionError(
                f"Provided Limit is out of bounds (Value: {limit}, Min: 1, Max: {table.max_limit})"
            )

    # Validate offset
    if offset := kwargs.get("offset"):
        if offset < 0:
            raise QueryExecutionError(
                f"Provided Offset is negative (Value: {offset}, Min: 0)"
            )


def build_async_resolver(table: Table):
    """
    Resolver function for Async queries.
    Returns a function that can be called at query execution to resolve query.
    """

    async def resolver(root, info, **kwargs):
        validations(table, **kwargs)

        db_session = info.context["session"]

        selection = info.field_nodes[0].selection_set

        query = build_sql_select_stmt(
            table=table.sqlalchemy_cls,
            columns=[f.name.value for f in selection.selections] if selection else [],
            filters=kwargs.get("filter", {}),
            offset=kwargs.get("offset", 0),
            limit=kwargs.get("limit", table.default_limit),
            order=kwargs.get("order", table.default_order),
        )

        res = await db_session.execute(query)

        return convert_enums(res.mappings().all())

    return resolver


def build_sync_resolver(table: Table):
    """
    Resolver function for Sync queries.
    Returns a function that can be called at query execution to resolve query.
    """

    def resolver(root, info, **kwargs):
        validations(table, **kwargs)

        db_session = info.context["session"]

        selection = info.field_nodes[0].selection_set

        query = build_sql_select_stmt(
            table=table.sqlalchemy_cls,
            columns=[f.name.value for f in selection.selections] if selection else [],
            filters=kwargs.get("filter", {}),
            offset=kwargs.get("offset", 0),
            limit=kwargs.get("limit", table.default_limit),
            order=kwargs.get("order", table.default_order),
        )

        res = db_session.execute(query)

        return convert_enums(res.mappings().all())

    return resolver
