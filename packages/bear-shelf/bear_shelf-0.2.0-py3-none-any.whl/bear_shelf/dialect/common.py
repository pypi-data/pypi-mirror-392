"""Common utilities and dataclasses for the Bear Shelf SQLAlchemy dialect."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from sqlalchemy.engine.url import URL

    from bear_shelf.datastore.storage import StorageChoices

TRUE_VALUES: tuple = (True, "auto")
"""Values that represent True for autoincrement."""

STORAGE_TO_EXT: dict[StorageChoices, str] = {
    "jsonl": ".jsonl",
    "json": ".json",
    "toml": ".toml",
    "xml": ".xml",
    "yaml": ".yaml",
    "memory": ":memory:",  # We use :memory: to indicate in-memory storage
}

EXT_TO_STORAGE: dict[str, StorageChoices] = {
    ".jsonl": "jsonl",
    ".json": "json",
    ".toml": "toml",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ":memory:": "memory",
}


class DialectInfo(NamedTuple):
    """Dataclass to store SQLAlchemy dialect information."""

    dialect: str = "bearshelf"
    """The name of the dialect."""
    param_style: str = "named"
    """The parameter style used by the dialect."""
    default_extension: str = ".jsonl"
    """The default file extension for database files."""
    ddl_comment_prefix: str = "/* bearshelf:"
    """The prefix for DDL comments in compiled statements."""
    module_path: str = "bear_shelf.dialect.bear_dialect"
    """The module path for the dialect."""
    class_name: str = "BearShelfDialect"
    """The class name of the dialect."""
    valid_storages: tuple[str, ...] = ("jsonl", "json", "toml", "xml", "yaml", "yml", "memory")
    """A tuple of valid storage backend types."""
    valid_extensions: tuple[str, ...] = (".jsonl", ".json", ".toml", ".xml", ".yaml", ".yml", ":memory:")
    """A tuple of valid file extensions for database files."""


INFO = DialectInfo()


def ensure_file_extension(path: Path, storage_type: StorageChoices) -> Path:
    """Ensure the database path has the correct extension for the storage type.

    Args:
        path (Path): The original database file path
        storage_type (StorageChoices): The storage backend type

    Returns:
        Path with the correct extension for the storage type
    """
    if storage_type == "memory":
        return path

    expected_ext: str = STORAGE_TO_EXT.get(storage_type, ".jsonl")

    if not path.suffix or path.suffix != expected_ext:
        return path.with_suffix(expected_ext)

    return path


class DatabasePathInfo(NamedTuple):
    """Dataclass to store database path information."""

    path: str
    """The database file path."""
    storage: StorageChoices
    """The storage backend type."""


class DBPathReturn(NamedTuple):
    """Dataclass to store database path return information."""

    path: list[str]
    """The database file path."""
    opts: dict[str, str]
    """The options dictionary."""


class Count(NamedTuple):
    """Result of a COUNT aggregate function."""

    n: int = 0


def get_database_path_from_url(url: URL, storage_type: StorageChoices = "jsonl") -> DatabasePathInfo:
    """Determine the database file path from the given URL.

    Args:
        url (URL): The SQLAlchemy database URL
        storage_type (StorageChoices): The storage backend type

    Returns:
        tuple[str, StorageChoices]: A tuple containing the database file path and storage type
    """
    if url.database and not url.host:
        database_path = Path(url.database)
    elif url.database and url.host:
        database_path: Path = (Path(url.host) / url.database).absolute()
    else:
        database_path = Path(f"./default{INFO.default_extension}")

    if database_path.suffix in INFO.valid_extensions:
        storage_type = EXT_TO_STORAGE[database_path.suffix]
    else:
        database_path = ensure_file_extension(database_path, storage_type)
    return DatabasePathInfo(str(database_path), storage_type)
