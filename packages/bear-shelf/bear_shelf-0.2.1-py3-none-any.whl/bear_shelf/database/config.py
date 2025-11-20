"""Database configuration utilities."""

from pathlib import Path

from pydantic import SecretStr  # noqa: TC002

from bear_shelf.datastore.storage import StorageChoices  # noqa: TC001
from bear_shelf.models import Password

from .schemas import DatabaseConfig, DBConfig, Schemas, get_defaults


def get_default_config(
    schema: Schemas,
    host: str | None = None,
    port: int | None = None,
    name: str | None = None,
    path: str | None = None,
    user: str | None = None,
    password: str | SecretStr | None = None,
) -> DatabaseConfig:
    """Get the default database configuration for a given scheme."""
    defaults: DBConfig = get_defaults(schema)
    return DatabaseConfig(
        scheme=schema,
        host=host or defaults.host,
        port=port or defaults.port,
        name=name or defaults.name,
        path=path or (defaults.name if schema == "sqlite" else None),
        username=user or defaults.username,
        password=Password.load(password) if password else None,
    )


def sqlite_memory_db() -> DatabaseConfig:
    """Get a SQLite in-memory database configuration."""
    return DatabaseConfig(scheme="sqlite", name=":memory:")


def sqlite_default_db() -> DatabaseConfig:
    """Get a SQLite default database configuration."""
    return get_default_config(schema="sqlite")


def mysql_default_db() -> DatabaseConfig:
    """Get a MySQL default database configuration."""
    return get_default_config(schema="mysql")


def postgres_default_db() -> DatabaseConfig:
    """Get a PostgreSQL default database configuration."""
    return get_default_config(schema="postgresql")


PossibleStorages: dict[str, StorageChoices] = {
    ".jsonl": "jsonl",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".xml": "xml",
    ".toml": "toml",
    ".msgpack": "msgpack",
}


def bearshelf_default_db(
    path: Path | str = "database",
    storage: StorageChoices | None = None,
) -> DatabaseConfig:
    """Get a BearShelf default database configuration.

    Args:
        path: Path to the database file. The file extension determines the storage format:
              - .jsonl: JSON Lines format (default)
              - .json: JSON format
              - .yaml or .yml: YAML format
              - .xml: XML format
              - .toml: TOML format
        storage: Optional storage backend specification.


    Returns:
        DatabaseConfig: A BearShelf database configuration.
    """
    if storage is None or storage not in PossibleStorages.values():
        storage = PossibleStorages.get(Path(path).suffix.lower(), "jsonl")
    path = Path(path).with_suffix(f".{storage}")
    return get_default_config(schema="bearshelf", path=str(path))


__all__ = [
    "bearshelf_default_db",
    "get_default_config",
    "mysql_default_db",
    "postgres_default_db",
    "sqlite_default_db",
    "sqlite_memory_db",
]
