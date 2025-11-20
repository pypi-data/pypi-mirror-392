"""Executor for DML operations in BearShelf dialect."""

from typing import TYPE_CHECKING, Any

from bear_shelf.datastore.record import Record, Records
from bear_shelf.dialect import protocols as pro
from bear_shelf.dialect.descript import get_descriptor
from bear_shelf.dialect.helpers import _aggregate_functions as agg, _extract_values as ext
from funcy_bear.sentinels import MISSING, MissingType

type Compiled = pro.CompiledStatement

if TYPE_CHECKING:
    from sqlalchemy import Delete, Insert, Table, Update

    from bear_shelf.datastore.tables.table import Table as BearTable
    from bear_shelf.dialect.bear_dialect import BearShelfDialect
    from bear_shelf.dialect.cursor import BearCursor
    from funcy_bear.query import QueryInstance

type Results = list[tuple[Any, ...]]


class DMLExecutor:
    """Handles DML (INSERT/UPDATE/DELETE) operations."""

    def __init__(self, dialect: Any) -> None:
        """Initialize DMLExecutor with dialect reference."""
        self.dialect: BearShelfDialect = dialect

    def execute_select(self, compiled: Compiled, cursor: BearCursor, parameters: Any) -> Results:
        """Execute SELECT statement."""
        statement: Any | None = compiled.statement
        table_name: str | None = ext.extract_table_name(statement)
        if table_name is None:
            return []
        table: BearTable | MissingType = self.get_table(table_name, cursor, reset=False)
        if isinstance(table, MissingType):
            return []

        agg_result: agg.Count | None = agg.aggregate_functions(statement, self.dialect.base, table_name, parameters)
        if agg_result is not None:
            cursor.set_descriptor(name="count_1")
            return [agg_result]

        where_clause: QueryInstance | None = agg._translate_where_clause(statement, parameters)

        order_by_info: list[tuple[str, bool]] = ext.extract_order_by(statement)
        bear_records: list[Record] = self.dialect._get_records(table, order_by_info, where_clause)
        records_obj = Records(bear_records)

        # Apply OFFSET and LIMIT if present (order matters!)
        limit_value: int | None = ext.extract_limit(statement)
        offset_value: int | None = ext.extract_offset(statement)

        if offset_value is not None:
            records_obj: Records = records_obj.offset(offset_value)
        if limit_value is not None:
            records_obj = records_obj.limit(limit_value)

        records: list[dict[str, Any]] = [rec.model_dump() for rec in records_obj.all()]
        selected_columns: list[str] = ext.extract_selected_columns(statement)

        if ext.is_distinct(statement):
            records = (
                ext.single_col_distinct(records, selected_columns)
                if len(selected_columns) == 1
                else ext.multi_col_distinct(records, selected_columns)
            )

        def _get_row(record: dict[str, Any], selected_cols: list[str]) -> tuple[Any, ...]:
            if selected_cols:
                return tuple(record.get(col) for col in selected_cols)
            return tuple(record.values())

        results: Results = [_get_row(rec, selected_columns) for rec in records]

        if selected_columns and table_name:
            tbl: Table | None = self.dialect.get_table(table_name)
            cursor.set_descriptor(descriptor=get_descriptor(tbl, selected_columns))
        return results

    def execute_insert(self, compiled: Any | Compiled, cursor: BearCursor, parameters: Any) -> None:
        """Execute INSERT."""
        statement: Insert = compiled.statement
        table: BearTable | MissingType = self.get_table(statement.table.name, cursor, reset=False)
        if not parameters or isinstance(table, MissingType):
            cursor.reset_row_count()
            return

        primary_key_name: str | None = table.primary_key
        is_autoincrement: bool = table.table_data.is_auto if primary_key_name else False

        if isinstance(parameters, list):
            # TODO: Improve batch insert performance - currently inserts one-by-one causing O(n²) file writes
            # datastore has `Table.insert_all(records)` that does bulk insert, we recently added WAL support
            # so if we ensure WAL is enabled, then the insert will be much faster.

            # records = [Record(**params) for params in parameters]
            # table.insert_all(records)
            # cursor.set_last_row_id(records[-1][primary_key_name] if records else None)

            for params in parameters:
                if is_autoincrement and primary_key_name in params and params[primary_key_name] is None:
                    p: dict[str, Any] = {k: v for k, v in params.items() if k != primary_key_name}
                    record = Record(**p)
                else:
                    record = Record(**params)
                table.insert(record)
                if primary_key_name is not None and primary_key_name in record:
                    cursor.set_last_row_id(record[primary_key_name])
            cursor.set_row_count(len(parameters))
        elif isinstance(parameters, dict):
            if is_autoincrement and primary_key_name in parameters and parameters[primary_key_name] is None:
                parameters = {k: v for k, v in parameters.items() if k != primary_key_name}
            record = Record(**parameters)
            table.insert(record)
            cursor.set_row_count(1)
            if primary_key_name is not None and primary_key_name in record:
                cursor.set_last_row_id(record[primary_key_name])

    def execute_update(self, compiled: Compiled, cursor: BearCursor, parameters: Any) -> None:
        """Execute UPDATE."""
        statement: Update = compiled.statement
        assert isinstance(statement.table, pro.ColumnWithName)  # noqa: S101
        table: BearTable | MissingType = self.get_table(str(statement.table.name), cursor, reset=False)
        if isinstance(table, MissingType):
            cursor.reset_row_count()
            return
        updates: dict[str, Any] = ext.extract_update_values(statement, parameters)
        where_clause: QueryInstance | None = agg._translate_where_clause(statement, parameters)
        count: int = table.update(fields=updates, cond=where_clause)
        cursor.set_row_count(count)

    def execute_delete(self, compiled: Compiled, cursor: BearCursor, parameters: Any) -> None:
        """Execute DELETE."""
        statement: Delete = compiled.statement
        assert isinstance(statement.table, pro.ColumnWithName)  # noqa: S101
        table: BearTable | MissingType = self.get_table(str(statement.table.name), cursor, reset=False)
        if isinstance(table, MissingType):
            cursor.reset_row_count()
            return

        where_clause: QueryInstance | None = agg._translate_where_clause(statement, parameters)

        if where_clause is None:
            raise ValueError("DELETE requires WHERE clause for safety. Use DELETE WHERE 1=1 for all records.")

        count: int = table.delete(cond=where_clause)
        cursor.set_row_count(count)

    def get_table(self, table_name: str, cursor: BearCursor, reset: bool = True) -> BearTable | MissingType:
        """Guard: check table exists

        Args:
            table_name: Name of the table
            cursor: BearCursor instance
            reset: Whether to reset the cursor rowcount if table not found
        Returns:
            BearTable instance or MISSING sentinel if not found
        """
        if self.dialect.not_name_in_table(str(table_name)):
            if reset:
                cursor.reset_row_count()
            return MISSING
        return self.dialect.base.table(table_name)

    def do_execute(
        self,
        cursor: BearCursor,
        statement: str,
        parameters: Any | None = None,
        context: Any | None = None,
    ) -> Any:
        """Execute a statement against the data store."""
        if not (context and isinstance(context, pro.Compiled)):
            cursor.execute(statement, parameters or (), context=context)
            return cursor

        compiled: pro.CompiledStatement = context.compiled

        if isinstance(compiled, pro.CompiledStatement) and isinstance(compiled.statement, pro.SelectableStatement):
            results: list[tuple[Any, ...]] = self.execute_select(compiled, cursor, parameters)
            cursor.set_results(results)
            return cursor

        if isinstance(compiled, pro.InsertStatement) and compiled.isinsert:
            self.execute_insert(compiled, cursor, parameters)
            return cursor

        if isinstance(compiled, pro.UpdateStatement) and compiled.isupdate:
            self.execute_update(compiled, cursor, parameters)
            return cursor

        if isinstance(compiled, pro.DeleteStatement) and compiled.isdelete:
            self.execute_delete(compiled, cursor, parameters)
            return cursor
        return cursor
