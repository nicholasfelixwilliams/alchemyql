from dataclasses import dataclass
from enum import auto, Enum


class Order(Enum):
    ASC = auto()
    DESC = auto()


@dataclass
class Table:
    # fmt: off

    # Table details
    sqlalchemy_cls  : type 
    graphql_name    : str
    description     : str | None

    # Fields Details
    include_fields  : list[str] | None
    exclude_fields  : list[str]

    # Filtering Details
    filter_fields    : list[str]

    # Ordering Details
    order_fields    : list[str]
    default_order   : dict[str, Order] | None

    # Pagination Details
    pagination      : bool
    default_limit   : int | None
    max_limit       : int | None

    # fmt: on
