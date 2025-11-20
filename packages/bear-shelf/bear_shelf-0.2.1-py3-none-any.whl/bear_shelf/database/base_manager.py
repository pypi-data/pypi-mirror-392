"""Database Manager Module for managing database connections and operations."""

from __future__ import annotations

from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar, Literal, overload

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, scoped_session, sessionmaker
from sqlalchemy.orm.session import Session

from ._extra import DatabaseManagerMeta, DynamicRecords
from .config import DatabaseConfig, Schemas, get_default_config

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy.orm.session import Session


def get_name(obj: str | type) -> str:
    """Get the name of a class or return the string if already a string.

    Args:
        obj (str | type): The class or string to get the name from.

    Returns:
        str: The name of the class or the string itself.
    """
    if isinstance(obj, str):
        return obj
    return obj.__name__


class DatabaseManager[T_Table](metaclass=DatabaseManagerMeta, bypass=False):
    """A class to manage database connections and operations."""

    _scheme: ClassVar[Schemas] = "sqlite"
    config_factory: partial[DatabaseConfig]
    engine_factory: partial[Engine]

    @classmethod
    def set_base(cls, base: DeclarativeMeta | None) -> None:
        """Set the base class for this database class."""
        cls._set_base(base)

    @classmethod
    def get_base(cls) -> DeclarativeMeta:
        """Get the base class for this database class."""
        if cls._base is None:
            cls._set_base(declarative_base())
        return cls._get_base()

    @classmethod
    def clear_base(cls) -> None:
        """Clear the base class for this database class."""
        cls._set_base(None)

    @classmethod
    def set_scheme(cls, scheme: Schemas) -> None:
        """Set the default scheme for the database manager."""
        cls._scheme = scheme

    def __init__(self, **kwargs) -> None:
        """Initialize the DatabaseManager with a database URL or connection parameters.

        Args:
            database_config (DatabaseConfig | None): The database configuration object.
            host (str): The database host.
            port (int): The database port.
            user (str): The database username.
            password (str | SecretStr): The database password.
            name (str): The database name.
            path (str | None): The database file path (for SQLite).
            schema (Schemas | None): The database schema/type (e.g., 'sqlite', 'postgresql', 'mysql').
            engine (Engine | None): An optional SQLAlchemy Engine instance.
            auto: (bool): Whether to automatically create the engine and tables.
            enable_wal (bool): Whether to enable Write-Ahead Logging (WAL) for SQLite databases.
            flush_mode (WALFlushMode): The WAL flush mode.
            engine_create (bool): Whether to create a new engine if one is not provided.
            tables_create (bool): Whether to create tables on initialization.
            records (dict[str, type[T_Table]] | None): An optional dictionary of pre-registered dynamic records.
        """
        self.dynamic_records: dict[str, DynamicRecords] = {}
        self.metadata: MetaData = self.get_base().metadata

        self._config: DatabaseConfig | None = None
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None
        self._session: scoped_session[Session] | None = None

        self._on_init(
            config=kwargs.pop("database_config", None),
            schema=kwargs.pop("schema", None),
            engine=kwargs.pop("engine", None),
            auto=kwargs.pop("auto", False),
            engine_create=kwargs.pop("engine_create", False),
            tables_create=kwargs.pop("tables_create", False),
            records=kwargs.pop("records", {}),
            **kwargs,
        )

    def _on_init(
        self,
        records: dict[str, type[T_Table]] | None = None,
        config: DatabaseConfig | None = None,
        schema: Schemas | None = None,
        engine: Engine | None = None,
        auto: bool = False,
        engine_create: bool = False,
        tables_create: bool = False,
        **kwargs,
    ) -> None:
        """Hook method called after initialization.

        Args:
            records (dict[str, type[T_Table]] | None): An optional dictionary of pre-registered dynamic records.
            engine (Engine | None): An optional SQLAlchemy Engine instance.
        """
        if auto:
            engine_create = True
            tables_create = True

        self.config_factory = partial(
            get_default_config,
            schema=schema or self._scheme,
            user=kwargs.pop("user", None),
            password=kwargs.pop("password", None),
            host=kwargs.pop("host", None),
            port=kwargs.pop("port", None),
            name=kwargs.pop("name", None),
            path=kwargs.pop("path", None),
        )

        if config is not None:
            self._config = config

        self.engine_factory: partial[Engine] = partial(
            create_engine, self.config.db_url.get_secret_value(), echo=False, connect_args={**kwargs}
        )

        if engine_create or engine is None:
            self._engine = engine or self.engine_factory()
        if tables_create:
            self.create_tables()

        if records:
            for rec_name, rec_cls in records.items():
                self.register_records(tbl_obj=rec_cls, name=rec_name)

    def register_records(self, tbl_obj: type[T_Table], name: str | None = None) -> DynamicRecords[T_Table]:
        """Register a table class for dynamic record access.

        Args:
            name (str): The name to register the table class under.
            tbl_obj (type[T]): The table class to register.

        Returns:
            DynamicRecords[T]: An instance of DynamicRecords for the table class.
        """
        name = get_name(tbl_obj) if name is None else name

        if name in self.dynamic_records:
            raise ValueError(f"Records for {name} are already registered.")
        records: DynamicRecords[T_Table] = DynamicRecords(tbl_obj=tbl_obj, session=self.session)
        self.dynamic_records[name] = records
        return records

    def is_registered(self, name: str | type) -> bool:
        """Check if a table class is registered.

        Args:
            name (str | type): The name of the registered table class or the class itself.

        Returns:
            bool: True if the table class is registered, False otherwise.
        """
        return get_name(name) in self.dynamic_records

    def clear_records(self) -> None:
        """Clear all registered dynamic records."""
        self.dynamic_records.clear()

    def get_all[T_Table](self, name: str | type[T_Table]) -> list[T_Table]:  # type: ignore[override]
        """Get all records from a table.

        Args:
            name (str): The name of the registered table class.

        Returns:
            list[T_Table]: A list of all records in the table.
        """
        name = get_name(name)
        if name not in self.dynamic_records:
            raise ValueError(f"Records for {name} are not registered.")
        records: DynamicRecords[T_Table] = self.dynamic_records[name]
        return records.all()

    def count(self, o: str | type[T_Table], **kwargs) -> int:
        """Count the number of records in a table.

        Args:
            name (str): The name of the registered table class.

        Returns:
            int: The count of records in the table.
        """
        name: str = get_name(o)
        if name not in self.dynamic_records:
            raise ValueError(f"Records for {name} are not registered.")
        records: DynamicRecords[T_Table] = self.dynamic_records[name]
        return records.count() if not kwargs else len(records.filter_by(**kwargs))

    def get(self, o: str | type[T_Table], **kwargs) -> list[T_Table]:  # type: ignore[override]
        """Get records from a table by a specific variable.

        Args:
            name (str): The name of the registered table class.
            **kwargs: The variable/column name and value to filter by.

        Returns:
            list[T_Table]: A list of records matching the filter.
        """
        name: str = get_name(o)
        if name not in self.dynamic_records:
            raise ValueError(f"Records for {name} are not registered.")
        records: DynamicRecords[T_Table] = self.dynamic_records[name]
        return records.filter_by(**kwargs)

    @overload
    def get_session(self, scoped: Literal[True]) -> scoped_session: ...

    @overload
    def get_session(self, scoped: Literal[False] = False) -> Session: ...

    def get_session(self, scoped: bool = False) -> scoped_session | Session:
        """Get the scoped session for this database class.

        Args:
            scoped (bool): Whether to return a scoped session or a regular session.

        Returns:
            scoped_session | Session: The scoped session or regular session.
        """
        if self.instance_session is None:
            self.instance_session = scoped_session(self.session_factory)
        return self.instance_session if scoped else self.instance_session()

    def set_session(self, session: scoped_session) -> None:
        """Set the scoped session for this database class."""
        self.instance_session = session

    @contextmanager
    def open_session(self) -> Generator[Session, Any]:
        """Provide a transactional scope around a series of operations.

        Will commit the session if no exceptions occur, otherwise will rollback.

        Yields:
            Generator[Session, Any]: A SQLAlchemy Session instance.
        """
        session: Session = self.session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    def close_session(self) -> None:
        """Close the session."""
        if self.instance_session is not None:
            self.session.remove()
        self.instance_session = None

    def create_tables(self) -> None:
        """Create all tables defined by Base"""
        self.metadata.create_all(self.engine)

    def debug_tables(self) -> dict[str, Any]:
        """Get the tables defined in the metadata."""
        base: DeclarativeMeta = self.get_base()
        return base.metadata.tables

    def close(self) -> None:  # Changing to use this method name since it's more intuitive and standard.
        """Close the session and connection."""
        self.close_session()
        if self._session_factory is not None:
            self._session_factory.close_all()
            self._session_factory = None
        if self.engine is not None:
            self.engine.dispose()
            self._engine = None

    @property
    def config(self) -> DatabaseConfig:
        """Get the database configuration."""
        if self._config is None:
            self._config = self.config_factory()
        return self._config

    @property
    def engine(self) -> Engine:
        """Get the SQLAlchemy Engine."""
        if self._engine is None:
            self._engine = self.engine_factory()
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        """Get the session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory

    @property
    def instance_session(self) -> scoped_session | None:
        """Get the scoped session for this database class."""
        return self.__class__._scoped_session

    @instance_session.setter
    def instance_session(self, value: scoped_session | None) -> None:
        self.__class__._scoped_session = value

    @property
    def session(self) -> scoped_session[Session]:
        """Get the scoped session for this database class."""
        return self.get_session(scoped=True)

    def __enter__(self) -> DatabaseManager[T_Table]:
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the runtime context related to this object."""
        self.close()


class SqliteDB[T](DatabaseManager[T]):
    """SQLite Database Manager, inherits from DatabaseManager and sets the scheme to sqlite."""

    _scheme: ClassVar[Schemas] = "sqlite"


class PostgresDB[T](DatabaseManager[T]):
    """Postgres Database Manager, inherits from DatabaseManager and sets the scheme to postgresql."""

    _scheme: ClassVar[Schemas] = "postgresql"


class MySQLDB[T](DatabaseManager[T]):
    """MySQL Database Manager, inherits from DatabaseManager and sets the scheme to mysql."""

    _scheme: ClassVar[Schemas] = "mysql"


class BearShelfDB[T](DatabaseManager[T]):
    """BearShelf Database Manager, inherits from DatabaseManager and sets the scheme to bearshelf.

    BearShelf uses file-based storage with multiple format options (JSONL, JSON, YAML, XML, TOML).
    The format is determined by the file extension in the database path/name.
    """

    _scheme: ClassVar[Schemas] = "bearshelf"


# NOTE: Instead of using a SingletonDB directly, you can import SingletonWrap and wrap any of the above classes.
#
# Example:
# from singleton_base import SingletonWrap
# from bear_utils.database import PostgresDB
# PostgresSingleton = SingletonWrap(PostgresDB, host='localhost', user='user', password='pass', name='dbname')
# db_instance = PostgresSingleton.get()


__all__ = ["BearShelfDB", "DatabaseManager", "MySQLDB", "PostgresDB", "SqliteDB"]
