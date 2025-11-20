"""Test that bear-shelf works with multiple storage formats."""

from pathlib import Path

import pytest
from sqlalchemy import Boolean, Engine, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """Base class for ORM models."""


class User(Base):
    """User model for testing."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


STORAGE_TYPES: list[str] = ["jsonl", "json", "xml", "yaml"]


@pytest.fixture
def data_dir() -> Path:
    """Get or create the test data directory."""
    data_path: Path = Path(__file__).parent / "data"
    data_path.mkdir(exist_ok=True)
    return data_path


@pytest.mark.parametrize("storage_type", STORAGE_TYPES)
def test_create_sample_database(storage_type: str, data_dir: Path):
    """Create a sample database for each storage type."""
    db_file: Path = data_dir / f"sample_database.{storage_type}"

    # Remove existing file if it exists
    if db_file.exists():
        db_file.unlink()

    engine: Engine = create_engine(f"bearshelf:///{db_file}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        users = [
            User(id=1, name="Bear", email="bear@example.com", is_active=True),
            User(id=2, name="Claire", email="claire@example.com", is_active=True),
            User(id=3, name="Shannon", email="shannon@example.com", is_active=False),
        ]
        session.add_all(users)
        session.commit()
    assert db_file.exists(), f"Database file {db_file} was not created"

    with Session(engine) as session:
        result: User | None = session.query(User).filter_by(name="Bear").first()
        assert result is not None
        assert result.email == "bear@example.com"
        assert result.is_active is True


@pytest.mark.parametrize("storage_type", STORAGE_TYPES)
def test_read_from_existing_database(storage_type: str, data_dir: Path):
    """Test reading from an existing database of each storage type."""
    db_file: Path = data_dir / f"sample_database.{storage_type}"
    if not db_file.exists():
        pytest.skip(f"Sample database {db_file} not found - run test_create_sample_database first")
    engine: Engine = create_engine(f"bearshelf:///{db_file}")

    # Read and verify data
    with Session(engine) as session:
        users: list[User] = session.query(User).all()
        assert len(users) == 3

        names: set[str] = {user.name for user in users}
        assert names == {"Bear", "Claire", "Shannon"}

        # Test filtering
        active_users: list[User] = session.query(User).filter_by(is_active=True).all()
        assert len(active_users) == 2


def test_all_storage_types_work(data_dir: Path) -> None:
    """Integration test ensuring all storage types are functional."""
    for storage_type in STORAGE_TYPES:
        db_file: Path = data_dir / f"integration_test.{storage_type}"

        if db_file.exists():
            db_file.unlink()

        engine: Engine = create_engine(f"bearshelf:///{db_file}")
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            user = User(name="TestUser", email="test@example.com", is_active=True)
            session.add(user)
            session.commit()

            result: User | None = session.query(User).first()
            assert result is not None
            assert result.name == "TestUser"

        if db_file.exists():
            db_file.unlink()
