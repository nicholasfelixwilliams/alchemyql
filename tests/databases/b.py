"""
Test Database B.

Simple database with 3 tables in it. These tables has every data type supported by Alchemy QL but features no relationships between tables.
"""

from datetime import date, datetime, time
from enum import Enum
from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class SampleEnum(Enum):
    ODD = 1
    EVEN = 2


class B_Table_1(Base):
    __tablename__ = "SAMPLE_TABLE_1"

    string_field: Mapped[str]
    int_field: Mapped[int] = mapped_column(primary_key=True)
    float_field: Mapped[float]
    bool_field: Mapped[bool]
    date_field: Mapped[date]
    datetime_field: Mapped[datetime]
    time_field: Mapped[time]
    bytes_field: Mapped[bytes]
    json_field: Mapped[dict] = mapped_column(JSON)
    enum_field: Mapped[SampleEnum]


class B_Table_2(Base):
    __tablename__ = "SAMPLE_TABLE_2"

    string_field: Mapped[str]
    int_field: Mapped[int] = mapped_column(primary_key=True)
    float_field: Mapped[float]
    bool_field: Mapped[bool]
    date_field: Mapped[date]
    datetime_field: Mapped[datetime]
    time_field: Mapped[time]
    bytes_field: Mapped[bytes]
    json_field: Mapped[dict] = mapped_column(JSON)
    enum_field: Mapped[SampleEnum]


class B_Table_3(Base):
    __tablename__ = "SAMPLE_TABLE_3"

    string_field: Mapped[str]
    int_field: Mapped[int] = mapped_column(primary_key=True)
    float_field: Mapped[float]
    bool_field: Mapped[bool]
    date_field: Mapped[date]
    datetime_field: Mapped[datetime]
    time_field: Mapped[time]
    bytes_field: Mapped[bytes]
    json_field: Mapped[dict] = mapped_column(JSON)
    enum_field: Mapped[SampleEnum]
