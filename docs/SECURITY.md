# Security Notes

AlchemyQL creates a read-only GraphQL API from registered SQLAlchemy models. Read-only access still needs deliberate exposure controls because GraphQL clients can inspect schemas, traverse relationships, and request large result sets.

## Exposure Controls

Prefer `include_fields` for public APIs. This avoids exposing a newly added database column just because the SQLAlchemy model changed.

Use `exclude_fields` only when the default behavior of exposing all fields is acceptable for the table.

Register only relationships that callers should be allowed to traverse. Relationship traversal can reveal adjacent data even when a table is not directly queryable.

## Query Controls

Set `max_query_depth` on engines that are reachable by untrusted clients.

Enable pagination for list queries and set `default_limit` and `max_limit`. This helps prevent accidental or intentional large scans.

Keep `filter_fields` and `order_fields` limited to fields that are safe to reveal and efficient to query. Prefer indexed fields for high-traffic APIs.

## Application Controls

AlchemyQL does not perform authentication or authorization by itself. Add those controls in the application layer. For FastAPI, pass an `auth_dependency` to the router factory.

Avoid registering tables that contain secrets, credentials, tokens, or other high-sensitivity values. If those tables must be registered, expose a narrow `include_fields` list and review relationships carefully.
