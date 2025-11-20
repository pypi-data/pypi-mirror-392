"""Tests for DROP TABLE DDL operations."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, Integer, String, create_engine
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column

Base = declarative_base()


class User(Base):
    """Test user model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)


class Product(Base):
    """Test product model."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    """Create test engine with bear-shelf dialect."""
    db_path: Path = tmp_path / "test.jsonl"
    return create_engine(f"bearshelf:///{db_path}")


def test_drop_single_table(engine: Engine) -> None:
    """Test dropping a single table."""
    Base.metadata.create_all(engine, tables=[User.__table__])

    # Verify table exists
    assert engine.dialect.has_table(engine.connect(), "users")

    # Drop table
    Base.metadata.drop_all(engine, tables=[User.__table__])

    # Verify table is gone
    assert not engine.dialect.has_table(engine.connect(), "users")


def test_drop_all_tables(engine):
    """Test dropping all tables."""
    # Create both tables
    Base.metadata.create_all(engine)

    # Verify tables exist
    conn = engine.connect()
    assert engine.dialect.has_table(conn, "users")
    assert engine.dialect.has_table(conn, "products")

    # Drop all tables
    Base.metadata.drop_all(engine)

    # Verify all tables are gone
    conn = engine.connect()
    assert not engine.dialect.has_table(conn, "users")
    assert not engine.dialect.has_table(conn, "products")


def test_drop_nonexistent_table(engine: Engine) -> None:
    """Test dropping a table that doesn't exist (should not raise error)."""
    # Try to drop without creating - should be safe
    Base.metadata.drop_all(engine, tables=[User.__table__])

    # Verify table still doesn't exist
    assert not engine.dialect.has_table(engine.connect(), "users")


def test_create_drop_recreate(engine: Engine) -> None:
    """Test creating, dropping, and recreating a table."""
    # Create table and add data
    Base.metadata.create_all(engine, tables=[User.__table__])

    with Session(engine) as session:
        session.add(User(name="Alice"))
        session.commit()

        # Verify data exists
        users: list[User] = session.query(User).all()
        assert len(users) == 1

    # Drop table
    Base.metadata.drop_all(engine, tables=[User.__table__])
    assert not engine.dialect.has_table(engine.connect(), "users")

    # Recreate table
    Base.metadata.create_all(engine, tables=[User.__table__])
    assert engine.dialect.has_table(engine.connect(), "users")

    # Verify table is empty
    with Session(engine) as session:
        users = session.query(User).all()
        assert len(users) == 0


def test_drop_specific_table_leaves_others(engine: Engine) -> None:
    """Test dropping one table doesn't affect others."""
    # Create both tables
    Base.metadata.create_all(engine)

    # Add data to both
    with Session(engine) as session:
        session.add(User(name="Alice"))
        session.add(Product(name="Widget", price=100))
        session.commit()

    # Drop only users table
    Base.metadata.drop_all(engine, tables=[User.__table__])

    # Verify users is gone but products remains
    conn = engine.connect()
    assert not engine.dialect.has_table(conn, "users")
    assert engine.dialect.has_table(conn, "products")

    # Verify products data is intact
    with Session(engine) as session:
        products: list[Product] = session.query(Product).all()
        assert len(products) == 1
        assert products[0].name == "Widget"
