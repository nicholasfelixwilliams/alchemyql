from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLNonNull,
)
from sqlalchemy import inspect

from .errors import ConfigurationError
from .filters import convert_to_filter
from .models import Table
from .resolver import build_async_resolver, build_sync_resolver
from .scalars import convert_to_scalar, IntScalar, OrderingEnumScalar


def _validate_table(table: Table, inspected):
    """
    Perform validations on the table registered. Validations include:
     - Checking all fields exist
     - Checking all types are supported

    Any failed validations causes an exception to be thrown.
    """
    # Check all fields exist
    for field in (
        set(table.include_fields or [])
        | set(table.exclude_fields)
        | set(table.filter_fields)
        | set(table.order_fields)
        | (set(table.default_order.keys()) if table.default_order else set())
    ):
        if field not in inspected.columns:
            raise ConfigurationError(
                f"Field {field} does not exist in {table.graphql_name}!"
            )


def build_gql_schema(tables: list[Table], is_async: bool) -> GraphQLSchema:
    # Mapping of types to scalars
    scalar_map = {}

    # Step 1 - Build list of table schemas
    table_schemas: dict[str, GraphQLField] = {}

    for table in tables:
        inspected = inspect(table.sqlalchemy_cls)

        _validate_table(table, inspected)

        fields = {}
        query_fields = {}

        for col in inspected.columns:
            if col.type.python_type in scalar_map:
                ql_type = scalar_map[col.type.python_type]
            else:
                ql_type = convert_to_scalar(col)
                scalar_map[col.type.python_type] = ql_type

            if col.key not in table.exclude_fields and (
                not table.include_fields or col.key in table.include_fields
            ):
                if col.nullable:
                    fields[col.key] = GraphQLField(ql_type)  # type: ignore
                else:
                    fields[col.key] = GraphQLField(GraphQLNonNull(ql_type))  # type: ignore

            if col.key in table.filter_fields:
                query_fields[col.key] = convert_to_filter(col, ql_type)

        args = {}

        if query_fields:
            args["filter"] = GraphQLArgument(
                GraphQLInputObjectType(
                    name=f"{table.graphql_name}_filter", fields=lambda: query_fields
                )  # type: ignore
            )

        if table.pagination:
            args["limit"] = GraphQLArgument(
                IntScalar, default_value=table.default_limit
            )
            args["offset"] = GraphQLArgument(IntScalar, default_value=0)

        if table.order_fields:
            f = {it: GraphQLInputField(OrderingEnumScalar) for it in table.order_fields}
            args["order"] = GraphQLArgument(
                GraphQLInputObjectType(
                    name=f"{table.graphql_name}_order", fields=lambda: f
                )  # type: ignore
            )

        ql_table = GraphQLObjectType(
            name=table.graphql_name, description=table.description, fields=fields
        )

        table_schemas[table.graphql_name + "s"] = GraphQLField(
            GraphQLList(ql_table),
            resolve=build_async_resolver(table)
            if is_async
            else build_sync_resolver(table),
            args=args,
        )

    query = GraphQLObjectType(name="Query", fields=lambda: table_schemas)
    return GraphQLSchema(query=query)  # type: ignore
