"""
Test Database D.

Database with 3 tables in it. These tables features relationships between each other:
    - T1 - T2 (1-1)
    - T1 - T3 (1-many)
    - T2 - T3 (many-many)

Database style: SQL Alchemy declarative ORM (mapped).
"""

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase): ...


t2_t3_link = Table(
    "T2_T3_LINK",
    Base.metadata,
    Column("t2_id", ForeignKey("SAMPLE_TABLE_2.int_field"), primary_key=True),
    Column("t3_id", ForeignKey("SAMPLE_TABLE_3.int_field"), primary_key=True),
)


class D_Table_2(Base):
    __tablename__ = "SAMPLE_TABLE_2"

    int_field: Mapped[int] = mapped_column(primary_key=True)
    string_field: Mapped[str]

    # One-to-One backref from T1
    t1_rel: Mapped["D_Table_1"] = relationship(back_populates="t2_rel", uselist=False)

    # Many-to-many to T3
    t3_rel: Mapped[list["D_Table_3"]] = relationship(
        secondary=t2_t3_link,
        back_populates="t2_rel",
    )


class D_Table_1(Base):
    __tablename__ = "SAMPLE_TABLE_1"

    int_field: Mapped[int] = mapped_column(primary_key=True)
    string_field: Mapped[str]

    # One-to-One FK
    t2_int_field: Mapped[int] = mapped_column(
        ForeignKey("SAMPLE_TABLE_2.int_field"),
        unique=True,  # ensures 1-1
    )

    # Relationship to T2
    t2_rel: Mapped[D_Table_2] = relationship(back_populates="t1_rel")

    # One-to-many to T3
    t3_rel: Mapped[list["D_Table_3"]] = relationship(back_populates="t1_rel")


class D_Table_3(Base):
    __tablename__ = "SAMPLE_TABLE_3"

    int_field: Mapped[int] = mapped_column(primary_key=True)
    string_field: Mapped[str]

    # FK to T1 (one-to-many)
    t1_int_field: Mapped[int | None] = mapped_column(
        ForeignKey("SAMPLE_TABLE_1.int_field"),
        nullable=True,
    )

    # Backref to T1
    t1_rel: Mapped[D_Table_1 | None] = relationship(back_populates="t3_rel")

    # Many-to-many to T2
    t2_rel: Mapped[list[D_Table_2]] = relationship(
        secondary=t2_t3_link,
        back_populates="t3_rel",
    )
