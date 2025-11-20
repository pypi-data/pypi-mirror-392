"""A set of SQL compilers for the Bear Shelf dialect."""

from typing import Any

from sqlalchemy.sql import compiler

from bear_shelf.dialect.common import DialectInfo

info = DialectInfo()


class StatementCompiler(compiler.SQLCompiler):
    """SQL compiler for Bear Shelf dialect.

    We don't override visit_select - let the parent handle compilation.
    Our dialect will intercept execution in do_execute.
    """


class BearDDLCompiler(compiler.DDLCompiler):
    """DDL compiler for Bear Shelf dialect."""

    def visit_create_table(self, create: Any, **_) -> str:
        """Handle CREATE TABLE DDL - emit sentinel comment."""
        return f"{info.ddl_comment_prefix} create {create.element.name} */"

    def visit_drop_table(self, drop: Any, **_) -> str:
        """Handle DROP TABLE DDL - emit sentinel comment."""
        return f"{info.ddl_comment_prefix} drop {drop.element.name} */"
