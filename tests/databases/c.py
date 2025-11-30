"""
Test Database C.

Simple database with 1 table in it. This table has every data type supported by Alchemy QL.

Database style: traditional SQL Alchemy declarative ORM.
"""

from enum import Enum
from sqlalchemy import (
    JSON,
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Date,
    DateTime,
    Time,
    LargeBinary,
    Enum as SAEnum,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class SampleEnum(Enum):
    ODD = 1
    EVEN = 2


class C_Table(Base):
    __tablename__ = "SAMPLE_TABLE"

    string_field = Column(String)
    int_field = Column(Integer, primary_key=True)
    float_field = Column(Float)
    bool_field = Column(Boolean)
    date_field = Column(Date)
    datetime_field = Column(DateTime)
    time_field = Column(Time)
    bytes_field = Column(LargeBinary)
    json_field = Column(JSON)
    enum_field = Column(SAEnum(SampleEnum))
