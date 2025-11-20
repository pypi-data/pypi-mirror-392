"""API Module for Bear Shelf providing database and datastore access."""

from typing import TYPE_CHECKING

from lazy_bear import lazy

if TYPE_CHECKING:
    from funcy_bear.query import QueryInstance, QueryMapping, QueryObject, QueryProtocol, QueryUnified
    from funcy_bear.query.query_mapping import where as where_map
    from funcy_bear.query.query_object import where as where_obj

    from .database.base_manager import BearShelfDB, DatabaseManager, MySQLDB, PostgresDB, SqliteDB
    from .database.config import (
        DatabaseConfig,
        bearshelf_default_db,
        get_default_config,
        mysql_default_db,
        postgres_default_db,
        sqlite_default_db,
        sqlite_memory_db,
    )
    from .database.schemas import Schemas
    from .datastore.base_settings import BaseSettingsModel
    from .datastore.columns import Columns
    from .datastore.database import BearBase, JsonBase, JSONLBase, MsgPackBase, TomlBase, XMLBase, YamlBase
    from .datastore.record import NullRecord, NullRecords, Record, Records
    from .datastore.storage import StorageChoices
    from .datastore.tables.data import TableData
    from .datastore.tables.table import Table
    from .datastore.unified_data import UnifiedDataFormat

else:
    query = lazy("funcy_bear.query")
    QueryInstance, QueryMapping, QueryObject, QueryProtocol, QueryUnified = query.to(
        "QueryInstance", "QueryMapping", "QueryObject", "QueryProtocol", "QueryUnified"
    )
    where_map = lazy("funcy_bear.query.query_mapping").to("where")
    where_obj = lazy("funcy_bear.query.query_object").to("where")

    db = lazy("bear_shelf.database")
    BearShelfDB, DatabaseManager, MySQLDB, PostgresDB, SqliteDB = db.to(
        "BearShelfDB", "DatabaseManager", "MySQLDB", "PostgresDB", "SqliteDB"
    )
    config = lazy("bear_shelf.database.config")
    (
        DatabaseConfig,
        bearshelf_default_db,
        get_default_config,
        mysql_default_db,
        postgres_default_db,
        sqlite_default_db,
        sqlite_memory_db,
    ) = config.to(
        "DatabaseConfig",
        "bearshelf_default_db",
        "get_default_config",
        "mysql_default_db",
        "postgres_default_db",
        "sqlite_default_db",
        "sqlite_memory_db",
    )
    Schemas = lazy("bear_shelf.database.schemas").to("Schemas")

    BaseSettingsModel = lazy("bear_shelf.datastore.base_settings").to("BaseSettingsModel")
    Columns = lazy("bear_shelf.datastore.columns").to("Columns")
    datastore = lazy("bear_shelf.datastore.database")
    BearBase, JsonBase, JSONLBase, MsgPackBase, TomlBase, XMLBase, YamlBase = datastore.to(
        "BearBase",
        "JsonBase",
        "JSONLBase",
        "MsgPackBase",
        "TomlBase",
        "XMLBase",
        "YamlBase",
    )
    record = lazy("bear_shelf.datastore.record")
    NullRecord, NullRecords, Record, Records = record.to("NullRecord", "NullRecords", "Record", "Records")
    StorageChoices = lazy("bear_shelf.datastore.storage").to("StorageChoices")
    table_data = lazy("bear_shelf.datastore.tables.data")
    TableData = table_data.to("TableData")
    Table = lazy("bear_shelf.datastore.tables.table").to("Table")
    UnifiedDataFormat = lazy("bear_shelf.datastore.unified_data").to("UnifiedDataFormat")

__all__ = [
    "BaseSettingsModel",
    "BearBase",
    "BearShelfDB",
    "Columns",
    "DatabaseConfig",
    "DatabaseManager",
    "JSONLBase",
    "JsonBase",
    "MsgPackBase",
    "MySQLDB",
    "NullRecord",
    "NullRecords",
    "PostgresDB",
    "QueryInstance",
    "QueryMapping",
    "QueryObject",
    "QueryProtocol",
    "QueryUnified",
    "Record",
    "Records",
    "Schemas",
    "SqliteDB",
    "StorageChoices",
    "Table",
    "TableData",
    "TomlBase",
    "UnifiedDataFormat",
    "XMLBase",
    "YamlBase",
    "bearshelf_default_db",
    "get_default_config",
    "mysql_default_db",
    "postgres_default_db",
    "sqlite_default_db",
    "sqlite_memory_db",
    "where_map",
    "where_obj",
]
