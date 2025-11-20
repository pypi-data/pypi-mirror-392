"""Bear Shelf SQLAlchemy dialect implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from sqlalchemy import ColumnDefault, Connection, PoolProxiedConnection, Table, event
from sqlalchemy.engine.default import DefaultDialect

from bear_shelf.datastore.columns import Columns
from bear_shelf.dialect import protocols as pro
from bear_shelf.dialect.common import INFO, TRUE_VALUES, DatabasePathInfo, DBPathReturn, get_database_path_from_url
from bear_shelf.dialect.compilers import BearDDLCompiler, StatementCompiler
from bear_shelf.dialect.database_api import BearDBAPI
from bear_shelf.dialect.executor import DMLExecutor

from .helpers import _extract_values as ext

if TYPE_CHECKING:
    from sqlalchemy.engine import ConnectArgsType
    from sqlalchemy.engine.interfaces import DBAPIConnection
    from sqlalchemy.engine.url import URL

    from bear_shelf.datastore.database import BearBase
    from bear_shelf.datastore.record import Record
    from bear_shelf.datastore.tables.table import Table as BearTable
    from bear_shelf.dialect.cursor import BearCursor
    from funcy_bear.query import QueryInstance


@event.listens_for(Table, "before_create")
def _bear_before_create(table: Table, connection: Connection, **_) -> None:
    """Handle table creation via DDL events."""
    if connection.dialect.name == INFO.dialect:
        dialect: BearShelfDialect = connection.dialect  # pyright: ignore[reportAssignmentType]
        dialect._create_storage_file(table, connection)


@event.listens_for(Table, "before_drop")
def _bear_before_drop(table: Table, connection: Connection, **_) -> None:
    """Handle table drop via DDL events."""
    if connection.dialect.name == INFO.dialect:
        dialect: BearShelfDialect = connection.dialect  # pyright: ignore[reportAssignmentType]
        dialect._drop_storage_file(table, connection)


class BearShelfDialect(DefaultDialect):
    """SQLAlchemy dialect for Bear Shelf multi-format storage (JSONL, JSON, TOML)."""

    name: str = INFO.dialect
    driver: str = INFO.dialect
    supports_alter = False
    supports_pk_autoincrement = True
    supports_default_values = True
    supports_empty_insert = True
    supports_unicode_statements = True
    supports_unicode_binds = True
    supports_native_decimal = True
    supports_native_boolean = True
    supports_statement_cache = False  # TODO: Fix caching issue with LIMIT/OFFSET before re-enabling
    has_terminate = True
    default_paramstyle: str = INFO.param_style

    statement_compiler = StatementCompiler
    ddl_compiler = BearDDLCompiler

    def __init__(self, **kwargs) -> None:
        """Initialize the dialect."""
        super().__init__(**kwargs)

        self._db: BearBase | None = None
        self._dbapi: BearDBAPI = kwargs.get("dbapi", self.import_dbapi())
        self._tables: dict[str, Table] = {}
        self._executor = DMLExecutor(self)

    @classmethod
    def import_dbapi(cls) -> BearDBAPI:
        """Import the mock DBAPI module."""
        return BearDBAPI()

    @property
    def dbapi(self) -> BearDBAPI:
        """Get the DBAPI module."""
        if self._dbapi is None:
            self._dbapi = self.import_dbapi()
        return self._dbapi

    @dbapi.setter
    def dbapi(self, value: BearDBAPI) -> None:
        """Set the DBAPI module."""
        self._dbapi = value

    @property
    def base(self) -> BearBase:
        """Get the BearBase instance."""
        if self._db is None:
            self._db = self.dbapi.base
        return self._db

    @base.setter
    def base(self, value: BearBase) -> None:
        """Set the BearBase instance."""
        self._db = value

    def create_connect_args(self, url: URL) -> ConnectArgsType:
        """Parse the database URL to get the file path and infer storage type from extension.

        URL format: bearshelf:///path/to/file.{ext}
        Example: bearshelf:///./database.jsonl   (uses JSONL storage)
                 bearshelf:///./database.xml     (uses XML storage)
                 bearshelf:///./database.toml    (uses TOML storage)
        """
        db_info: DatabasePathInfo = get_database_path_from_url(url)
        return DBPathReturn(path=[db_info.path], opts={"storage": db_info.storage})

    def do_rollback(self, dbapi_connection: PoolProxiedConnection) -> None:
        """Handle rollback - calls to a no-op on the DBAPI connection."""
        dbapi_connection.rollback()

    def do_commit(self, dbapi_connection: PoolProxiedConnection) -> None:
        """Handle commit - write changes to storage file."""
        dbapi_connection.commit()

    def do_executemany(self, cursor: BearCursor, statement, parameters, context: Any = None) -> Any:  # noqa: ANN001 #type: ignore[override]
        """Execute many statements (for bulk operations)."""
        if context and isinstance(context, pro.InsertCompiled):
            compiled: pro.InsertCompiled | Any = context.compiled

            if compiled.isinsert:
                self._executor.execute_insert(compiled, cursor, parameters)
                return cursor
        cursor.executemany(statement, parameters)
        return cursor

    def do_execute(self, cursor: BearCursor, statement, parameters, context: Any = None) -> Any:  # noqa: ANN001 #type: ignore[override]
        """Execute a statement - DDL handled by events, SELECT handled here."""
        if isinstance(statement, str) and statement.startswith(INFO.ddl_comment_prefix):
            return cursor
        return self._executor.do_execute(cursor, statement, parameters, context)

    def do_terminate(self, dbapi_connection: DBAPIConnection) -> None:
        """Terminate the DBAPI connection."""
        self.do_close(dbapi_connection)

    def do_close(self, dbapi_connection: DBAPIConnection) -> None:
        """Close the DBAPI connection."""
        dbapi_connection.close()

    def _get_records(
        self,
        tbl: BearTable,
        order_by_info: list[tuple[str, bool]],
        where_clause: QueryInstance | None = None,
    ) -> list[Record]:
        """Retrieve records from the table applying WHERE and ORDER BY clauses."""
        if order_by_info:
            name, is_desc = order_by_info[0]  # Only apply the first ORDER BY clause for now
            if where_clause is None:
                return tbl.all(list_recs=False).order_by(name, desc=is_desc).all()
            return tbl.search(where_clause).order_by(name, desc=is_desc).all()
        return tbl.search(where_clause).all() if where_clause is not None else tbl.all()

    def _get_columns(self, table: Table) -> list[Columns]:
        cols: list[Columns] = []
        for c in table.columns:  # pyright: ignore[reportGeneralTypeIssues]
            col_type: str = ext.map_sqlalchemy_type(cast("str", c.type))
            auto_inc_literal: Literal[True] | None = (c.primary_key and c.autoincrement in TRUE_VALUES) or None
            default_value: Any = cast("ColumnDefault", c.default).arg if c.default is not None else None
            foreign_key: str | None = next(iter(c.foreign_keys)).target_fullname if c.foreign_keys else None
            cols.append(
                Columns.create(
                    name=c.name,
                    type=col_type,
                    default=0 if auto_inc_literal and default_value is None else default_value,
                    nullable=bool(c.nullable) if not c.primary_key else False,
                    primary_key=bool(c.primary_key),
                    autoincrement=auto_inc_literal,
                    unique=bool(c.unique),
                    comment=str(c.comment) if c.comment is not None else None,
                    foreign_key=foreign_key,
                )
            )
        return cols

    def _create_storage_file(self, table: Table, connection: Connection) -> None:  # noqa: ARG002
        """Create table in BearBase from SQLAlchemy Table."""
        table_name = str(table.name)
        self._tables[table_name] = table
        columns: list[Columns] = self._get_columns(table)
        try:
            if self.not_name_in_table(table_name):
                # TODO: Figure out how to pass settings from the SQLAlchemy Table to BearBase
                self.base.create_table(table_name, columns=columns, save=True, enable_wal=self.base.enable_wal)
        except Exception as e:
            raise RuntimeError(f"Failed to create table '{table_name}' in storage.") from e

    def _drop_storage_file(self, table: Table, connection: Connection) -> None:  # noqa: ARG002
        """Drop table from BearBase."""
        table_name = str(table.name)
        if self.name_in_table(table_name):
            self.base.drop_table(table_name)
            self._tables.pop(table_name, None)

    def not_name_in_table(self, name: str) -> bool:
        """Check if a table name does NOT exist in the database."""
        return not self.name_in_table(name)

    def name_in_table(self, name: str) -> bool:
        """Check if a table name exists in the database."""
        return name in self.base.tables()

    def get_table(self, table_name: str) -> Table | None:
        """Get the SQLAlchemy Table object for a given table name."""
        return self._tables.get(table_name)

    def has_table(self, connection: Connection, table_name: str, schema=None, **kw) -> bool:  # noqa: ARG002 ANN001
        """Check if a table exists."""
        return table_name in self.base.tables()


from sqlalchemy.dialects import registry  # noqa: E402

registry.register(INFO.dialect, INFO.module_path, INFO.class_name)
