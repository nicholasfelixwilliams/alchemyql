from alchemyql import AlchemyQLSync, AlchemyQLAsync
from alchemyql.engine import AlchemyQL
from alchemyql.errors import ConfigurationError
import pytest

from .databases.a import A_Table, Base as A_Base
from .databases.b import B_Table_1, B_Table_2, Base as B_Base


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
