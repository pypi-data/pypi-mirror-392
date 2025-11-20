"""Database Manager Module for managing database connections and operations."""

from .base_manager import BearShelfDB, DatabaseManager, MySQLDB, PostgresDB, SqliteDB
from .config import (
    DatabaseConfig,
    bearshelf_default_db,
    get_default_config,
    mysql_default_db,
    postgres_default_db,
    sqlite_default_db,
    sqlite_memory_db,
)
from .schemas import Schemas

__all__ = [
    "BearShelfDB",
    "DatabaseConfig",
    "DatabaseManager",
    "MySQLDB",
    "PostgresDB",
    "Schemas",
    "SqliteDB",
    "bearshelf_default_db",
    "get_default_config",
    "mysql_default_db",
    "postgres_default_db",
    "sqlite_default_db",
    "sqlite_memory_db",
]
