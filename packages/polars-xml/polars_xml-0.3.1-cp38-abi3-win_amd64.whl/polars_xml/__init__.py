from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from polars.plugins import register_plugin_function

if TYPE_CHECKING:
    from _typing import IntoExprColumn

LIB = Path(__file__).parent


def xpath(expr: IntoExprColumn, xpath: str | IntoExprColumn) -> pl.Expr:
    """
    Evaluate an XPath expression, returning the selection as a string.
    """
    return register_plugin_function(
        plugin_path=LIB,
        function_name="xpath",
        args=[expr, pl.lit(xpath) if isinstance(xpath, str) else xpath],
        is_elementwise=True,
    )
