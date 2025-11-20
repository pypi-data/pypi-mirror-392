from typing import TYPE_CHECKING, Any

from bear_shelf.dialect.common import Count
from bear_shelf.dialect.sql_translator import translate_where_clause

if TYPE_CHECKING:
    from sqlalchemy.sql.dml import Delete, Update
    from sqlalchemy.sql.selectable import Select

    from bear_shelf.datastore import BearBase
    from bear_shelf.datastore.tables.table import Table
    from funcy_bear.query import QueryInstance


def aggregate_functions(
    statement: Any,
    base: BearBase,
    table_name: str,
    parameters: dict[str, Any] | None,
) -> Count | None:
    """Check if statement contains aggregate functions and compute them.

    Returns:
        A tuple with the aggregate result, or None if no aggregates found.
    """
    if table_name not in base.tables() or not hasattr(statement, "selected_columns"):
        return Count(0)
    table: Table = base.table(table_name)
    for col in statement.selected_columns:
        if type_name_equals(col, "count"):
            where_clause: QueryInstance | None = _translate_where_clause(statement, parameters)
            return Count(len(table) if where_clause is None else table.search(where_clause).record_count())
    return None


def type_name_equals(obj: object, name: str) -> bool:
    """Check if the type name of a type object matches the given string."""
    return type(obj).__name__ == name


def _translate_where_clause(
    statement: Any | Select | Update | Delete,
    parameters: dict[str, Any] | None,
) -> QueryInstance | None:
    """Translate WHERE clause from statement to QueryMapping."""
    if not hasattr(statement, "_where_criteria") or not statement._where_criteria:
        return None
    where_expr: Any = statement._where_criteria[0]
    return translate_where_clause(where_expr, parameters)
