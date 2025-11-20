"""Bear Shelf dialect database API module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn

from sqlalchemy.engine.interfaces import DBAPIConnection, DBAPIModule

from bear_shelf.datastore import BearBase
from bear_shelf.datastore.wal.config import WAL_CONFIG_FIELDS, WALFlushMode
from bear_shelf.dialect.common import INFO
from bear_shelf.dialect.cursor import BearCursor

if TYPE_CHECKING:
    from bear_shelf.datastore.storage import StorageChoices


class StandardError(Exception):
    """Standard error class for Bear Shelf dialect."""


class BearConnection(DBAPIConnection):
    """Helper class to handle a connection to a Bear Shelf database."""

    def __init__(self, database_path: Path, base: BearBase) -> None:
        """Initialize the connection."""
        self.database_path: Path = database_path
        self.base: BearBase = base
        self.closed = False

    def close(self) -> None:
        """Close the connection."""
        self.base.close()
        self.closed = True

    def commit(self) -> None:
        """Commit changes - handled by dialect's do_commit."""
        self.base.commit()

    def cursor(self, *args: Any, **kwargs: Any) -> BearCursor:  # noqa: ARG002
        """Return a cursor object."""
        return BearCursor()

    def rollback(self) -> None:
        """Rollback changes - not implemented."""
        # TODO: Implement rollback support
        # We might be able to do this via WAL that BearBase supports
        # since we can just clear uncommitted changes from the WAL
        # and memory cache, but for now, we do nothing.

    def __getattr__(self, item: Any) -> NoReturn:
        raise AttributeError(f"BearConnection has no attribute '{item}'")

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)


class BearDBAPI(DBAPIModule):
    """DBAPI module for bear-shelf dialect."""

    enable_wal: bool
    flush_mode: WALFlushMode
    _base: BearBase
    paramstyle: str = INFO.param_style
    Error: Any = StandardError

    def connect(self, database_path: str, storage: StorageChoices, **kwargs) -> BearConnection:
        """Connect to the database."""
        path = Path(database_path)
        params: dict[str, Any] = {k: v for k, v in kwargs.items() if k in WAL_CONFIG_FIELDS}
        self.enable_wal = kwargs.pop("enable_wal", False)
        self.flush_mode = kwargs.pop("flush_mode", WALFlushMode.BUFFERED)
        self.base = BearBase(path, storage=storage, enable_wal=self.enable_wal, **params)
        existing_tables: set[str] = self.base.tables()
        if existing_tables:
            self.base.set_table(next(iter(existing_tables)))
        return BearConnection(path, self.base)

    @property
    def base(self) -> BearBase:
        """Get the BearBase instance."""
        return self._base

    @base.setter
    def base(self, value: BearBase) -> None:
        """Set the BearBase instance."""
        self._base: BearBase = value

    def __getattr__(self, item: Any) -> NoReturn:
        raise AttributeError(f"BearDBAPI has no attribute '{item}'")

    def __repr__(self) -> str:
        if self.base is not None:
            return (
                f"<BearDBAPI enable_wal={self.enable_wal}, flush_mode={self.flush_mode}, storage={self.base.storage}>"
            )
        return "<BearDBAPI uninitialized>"
