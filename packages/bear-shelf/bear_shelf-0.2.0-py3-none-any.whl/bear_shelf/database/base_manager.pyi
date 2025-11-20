from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, ClassVar, Literal, overload

from pydantic import SecretStr
from sqlalchemy import Engine
from sqlalchemy.orm import DeclarativeMeta, scoped_session
from sqlalchemy.orm.session import Session

from bear_shelf.datastore.wal.config import WALFlushMode

from ._extra import DatabaseManagerMeta, DynamicRecords
from .config import DatabaseConfig, Schemas

def get_name(obj: str | type) -> str: ...

class DatabaseManager[T_Table](metaclass=DatabaseManagerMeta, bypass=False):
    _scheme: ClassVar[Schemas] = "sqlite"

    @classmethod
    def set_base(cls, base: DeclarativeMeta | None) -> None: ...
    @classmethod
    def get_base(cls) -> DeclarativeMeta: ...
    @classmethod
    def clear_base(cls) -> None: ...
    @classmethod
    def set_scheme(cls, scheme: Schemas) -> None: ...
    def __init__(
        self,
        *,
        database_config: DatabaseConfig | None = None,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | SecretStr | None = None,
        name: str | None = None,
        path: str | None = None,
        schema: Schemas | None = None,
        engine: Engine | None = None,
        auto: bool = False,
        enable_wal: bool = False,
        flush_mode: WALFlushMode = ...,
        engine_create: bool = False,
        tables_create: bool = False,
        records: dict[str, type[T_Table]] | None = None,
    ) -> None: ...
    def register_records(self, tbl_obj: type[T_Table], name: str | None = None) -> DynamicRecords[T_Table]: ...
    def is_registered(self, name: str | type) -> bool: ...
    def get_all[T_Table](self, name: str | type[T_Table]) -> list[T_Table]: ...  # type: ignore[override]
    def count(self, o: str | type[T_Table], **kwargs) -> int: ...
    def get(self, o: str | type[T_Table], **kwargs) -> list[T_Table]: ...  # type: ignore[override]
    @property
    def instance_session(self) -> scoped_session | None: ...
    @instance_session.setter
    def instance_session(self, value: scoped_session | None) -> None: ...
    @overload
    def get_session(self, scoped: Literal[True]) -> scoped_session: ...
    @overload
    def get_session(self, scoped: Literal[False] = False) -> Session: ...
    def get_session(self, scoped: bool = False) -> scoped_session | Session: ...
    def set_session(self, session: scoped_session) -> None: ...
    @contextmanager
    def open_session(self) -> Generator[Session, Any]: ...
    def close_session(self) -> None: ...
    def create_tables(self) -> None: ...
    def debug_tables(self) -> dict[str, Any]: ...
    def close(self) -> None: ...
    def __enter__(self) -> DatabaseManager[T_Table]: ...
    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None: ...

class SqliteDB[T](DatabaseManager[T]):
    _scheme: ClassVar[Schemas] = "sqlite"

class PostgresDB[T](DatabaseManager[T]):
    _scheme: ClassVar[Schemas] = "postgresql"

class MySQLDB[T](DatabaseManager[T]):
    _scheme: ClassVar[Schemas] = "mysql"

class BearShelfDB[T](DatabaseManager[T]):
    _scheme: ClassVar[Schemas] = "bearshelf"

__all__ = ["BearShelfDB", "DatabaseManager", "MySQLDB", "PostgresDB", "SqliteDB"]
