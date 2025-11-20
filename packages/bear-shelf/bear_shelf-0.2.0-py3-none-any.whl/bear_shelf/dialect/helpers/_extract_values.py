from functools import partial
from typing import Any, cast

from sqlalchemy import ColumnCollection, ColumnElement, Select
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.elements import KeyedColumnElement, NamedColumn

from bear_shelf.dialect import protocols as pro
from funcy_bear.sentinels import CONTINUE, ContinueType
from funcy_bear.tools import Dispatcher
from funcy_bear.type_stuffs.validate import is_instance_of

col = Dispatcher("value")
params = Dispatcher("value")


@col.dispatcher()
def value_check(value: Any) -> Any:
    """Default value checker."""
    return value


@col.register(partial(is_instance_of, types=pro.ColumnWithKey))
def column_value_check(value: pro.ColumnWithKey) -> Any:
    """Extract value from ColumnWithKey."""
    return value.key


@col.register(partial(is_instance_of, types=pro.ColumnWithName))
def column_name_value_check(value: pro.ColumnWithName) -> Any:
    """Extract name from ColumnWithName."""
    return value.name


@params.dispatcher()
def params_check(value: Any, key: Any, updates: dict[str, Any]) -> Any:  # noqa: ARG001
    """Default params checker."""
    return CONTINUE


@params.register(partial(is_instance_of, types=pro.BindParameterWithEffectiveValue))
def bind_effective_value_check(value: pro.BindParameterWithEffectiveValue, key: str, updates: dict[str, Any]) -> Any:
    """Extract effective value from BindParameterWithEffectiveValue."""
    updates[key] = value.effective_value


@params.register(partial(is_instance_of, types=pro.BindParameterWithValue))
def bind_value_check(value: pro.BindParameterWithValue, key: str, updates: dict[str, Any]) -> Any:
    """Extract value from BindParameterWithValue."""
    updates[key] = value.value


def extract_update_values(statement: Update, parameters: dict[str, Any] | None) -> dict[str, Any]:
    """Extract SET clause values from UPDATE statement."""
    updates: dict[str, Any] = {}
    if isinstance(statement, Update) and statement._values:
        for column, value_expr in statement._values.items():
            column_key: Any = value_check(column)
            flow: Any | ContinueType = params_check(value_expr, column_key, updates)
            if flow is not CONTINUE and parameters and column_key in parameters:
                updates[column_key] = parameters[column_key]
    if not updates and parameters:
        updates = parameters.copy()
    return updates


def extract_selected_columns(statement: Any) -> list[str]:
    """Extract column names from SELECT statement."""
    columns: list[str] = []
    if not hasattr(statement, "selected_columns"):
        return columns
    for col in statement.selected_columns:
        if isinstance(col, ColumnCollection):
            for sub_col in col:
                columns.append(value_check(sub_col))
        elif isinstance(col, pro.ColumnWithName):
            columns.append(col.name)
    return columns


def extract_limit(statement: Any) -> int | None:
    """Extract LIMIT clause from SELECT statement."""
    if hasattr(statement, "_limit_clause") and statement._limit_clause is not None:
        limit_clause: ColumnElement = statement._limit_clause
        if hasattr(limit_clause, "value"):
            return int(cast("int", limit_clause.value))
        return int(cast("int", limit_clause))
    return None


def extract_offset(statement: Any) -> int | None:
    """Extract OFFSET clause from SELECT statement."""
    if isinstance(statement, pro.LimitOffsetClause) and statement._offset_clause is not None:
        offset_clause: ColumnElement = statement._offset_clause
        if hasattr(offset_clause, "value"):
            return int(cast("int", offset_clause.value))
        return int(cast("int", offset_clause))
    return None


def extract_order_by(statement: Any) -> list[tuple[str, bool]]:
    """Extract ORDER BY clause from SELECT statement.

    Returns:
        List of tuples (column_name, is_descending)
    """
    order_by_clauses: list[tuple[str, bool]] = []
    if isinstance(statement, pro.OrderByClause) and statement._order_by_clauses:
        for clause in statement._order_by_clauses:
            is_desc: bool = hasattr(clause, "modifier") and clause.modifier is not None
            col: ColumnElement = clause.element if hasattr(clause, "element") else clause
            if isinstance(col, KeyedColumnElement) and isinstance(col.key, str):
                order_by_clauses.append((col.key, is_desc))
            elif isinstance(col, NamedColumn) and isinstance(col.name, str):
                order_by_clauses.append((col.name, is_desc))
    return order_by_clauses


def extract_table_name(statement: Any | Select) -> str | None:
    """Extract table name from a statement."""
    if not hasattr(statement, "get_final_froms"):
        return None
    froms: Any = statement.get_final_froms()
    if not froms:
        return None
    table: Any = next(iter(froms))
    return table.name


def is_distinct(statement: Any) -> bool:
    """Check if SELECT statement has DISTINCT.

    Returns:
        True if DISTINCT is requested
    """
    return hasattr(statement, "_distinct") and statement._distinct


def single_col_distinct(records: list[dict[str, Any]], selected_columns: list[str]) -> list[dict[str, Any]]:
    """Return a DISTINCT version of the SELECT statement."""
    seen: set[Any] = set()
    unique_records: list[dict[str, Any]] = []
    col: str = selected_columns[0]
    for record in records:
        val: Any | None = record.get(col)
        # Handle unhashable types
        hashable_val = tuple(val) if isinstance(val, list) else val
        if hashable_val not in seen:
            seen.add(hashable_val)
            unique_records.append(record)
    return unique_records


def multi_col_distinct(records: list[dict[str, Any]], selected_columns: list[str]) -> list[dict[str, Any]]:
    """Return a DISTINCT version of the SELECT statement for multiple columns."""
    seen_tuples: set[tuple[Any, ...]] = set()
    unique_records: list[dict[str, Any]] = []
    for record in records:
        if selected_columns:
            key: tuple[Any | None, ...] = tuple(record.get(col) for col in selected_columns)
        else:
            # All columns (SELECT *)
            key = tuple(record.values())
        if key not in seen_tuples:
            seen_tuples.add(key)
            unique_records.append(record)
    return unique_records


SQLAlchemyTypeMapping: dict[str, str] = {
    "INTEGER": "int",
    "SMALLINT": "int",
    "BIGINT": "int",
    "VARCHAR": "str",
    "TEXT": "str",
    "BOOLEAN": "bool",
    "FLOAT": "float",
    "DECIMAL": "float",
}


def map_sqlalchemy_type(sqlalchemy_type: str) -> str:
    """Map SQLAlchemy types to string representations."""
    type_str: str = str(sqlalchemy_type).upper()
    return SQLAlchemyTypeMapping.get(type_str, "str")
