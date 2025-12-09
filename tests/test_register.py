import pytest

from alchemyql import AlchemyQLAsync, AlchemyQLSync, Order
from alchemyql.engine import AlchemyQL
from alchemyql.errors import ConfigurationError

from .databases.a import A_Table
from .databases.a import Base as A_Base
from .databases.b import B_Table_1, B_Table_2
from .databases.b import Base as B_Base
from .databases.c import C_Table
from .databases.d import D_Table_1


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_duplicate_table(cls: type[AlchemyQL]):
    engine = cls()

    engine.register(A_Table)

    with pytest.raises(ConfigurationError):
        engine.register(A_Table)


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_duplicate_graphql_name(cls: type[AlchemyQL]):
    engine = cls()

    engine.register(B_Table_1, graphql_name="TEST")

    with pytest.raises(ConfigurationError):
        engine.register(B_Table_2, graphql_name="TEST")


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_all_tables_a(cls: type[AlchemyQL]):
    engine = cls()

    engine.register_all_tables(A_Base)

    assert len(engine.tables) == 1


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_all_tables_b(cls: type[AlchemyQL]):
    engine = cls()

    engine.register_all_tables(B_Base)

    assert len(engine.tables) == 3


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_tables_c(cls: type[AlchemyQL]):
    engine = cls()

    engine.register(C_Table)

    assert len(engine.tables) == 1


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_invalid_column_ref(cls: type[AlchemyQL]):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.register(A_Table, include_fields=["does-not-exist"])


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
@pytest.mark.parametrize("field", ["bytes_field", "json_field"])
def test_register_invalid_filter_column(cls: type[AlchemyQL], field: str):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.register(A_Table, filter_fields=[field])


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_invalid_default_order(cls: type[AlchemyQL]):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.register(
            A_Table,
            order_fields=["int_field"],
            default_order={"string_field": Order.DESC},
        )


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_invalid_default_limit(cls: type[AlchemyQL]):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.register(A_Table, pagination=True, default_limit=-1)


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_invalid_max_limit(cls: type[AlchemyQL]):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.register(A_Table, pagination=True, max_limit=-1)


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
def test_register_invalid_limits(cls: type[AlchemyQL]):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.register(A_Table, pagination=True, max_limit=2, default_limit=3)


@pytest.mark.parametrize("cls", [AlchemyQLSync, AlchemyQLAsync])
@pytest.mark.parametrize("field", ["fake_rel", "t1_rel"])
def test_register_invalid_relationship(cls: type[AlchemyQL], field: str):
    engine = cls()

    with pytest.raises(ConfigurationError):
        engine.register(D_Table_1, relationships=[field])
