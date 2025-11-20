# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Parser definitions and constants.
"""

import ast
from typing import Any, Callable

from comopy.datatypes import Bool
from comopy.hdl import cat, rep

# Comment markers
#
COMMENT_OUTPUT_VARS = "// Variables for output ports"
COMMENT_LOCALPARAMS = "// Local parameters"
COMMENT_LOCALPARAMS_END = "// [MARKER] Local parameters"
COMMENT_OUTPUTS = "// Outputs"


# Automatic variable names
#
def auto_module_output(port_name: str) -> str:
    return f"__{port_name}_bits"


def auto_inst_input(inst_name: str, port_name: str) -> str:
    # Matches CIRCT's auto-generated instance output port names
    return f"_{inst_name}_{port_name}"


# Parser error messages and suggestions
#
FIX_BOOL = "Use Bool() to convert to boolean (Bits1)."
FIX_DEFAULT = "Add 'case _:' for default case (use 'pass' if empty)."
FIX_INT = "Use b<N>() for Bits constants, such as b2(0b01) or b8(0xFF)."
FIX_PARAM = "Use LocalParam() or ModuleParam() for parameters."
FIX_WIDTH = (
    "Use .ext(width), .S.ext(width), or slice [:width] to match widths."
)

# HDL symbols
HDL_SYMBOLS = {
    # System functions
    range,
    # HDL functions
    Bool,
    cat,
    rep,
}

HDL_BITS_REDUCE_PROPERTIES = {"AO", "NZ", "P", "Z"}
HDL_BITS_PROPERTIES = {"V", "S", "W", "N"} | HDL_BITS_REDUCE_PROPERTIES
HDL_BITS_METHODS = {"ext"}

# HDL constant names
HDL_CONSTANT_NAMES = {"FALSE", "TRUE", "ASC", "DESC"}

# AST operator name mapping
#
_ast_op_name_map = {
    # Boolean operators
    ast.And: "and",
    ast.Or: "or",
    # Binary operators
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.MatMult: "@",
    ast.Div: "/",
    ast.Mod: "%",
    ast.Pow: "**",
    ast.LShift: "<<",
    ast.RShift: ">>",
    ast.BitOr: "|",
    ast.BitXor: "^",
    ast.BitAnd: "&",
    ast.FloorDiv: "//",
    # Unary operators
    ast.Invert: "~",
    ast.Not: "not",
    ast.UAdd: "+",
    ast.USub: "-",
    # Comparison operators
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.Is: "is",
    ast.IsNot: "is not",
    ast.In: "in",
    ast.NotIn: "not in",
}


def ast_op_name(op: ast.AST) -> str:
    """Get the string representation of an AST operator."""
    op_type = type(op)
    if op_type in _ast_op_name_map:
        return _ast_op_name_map[op_type]
    return op_type.__name__


# AST operator evaluation functions for constant folding
# Supports integer arguments only.
#
_ast_eval_func_map: dict[type[ast.AST], Callable[..., Any]] = {
    # Boolean operators
    ast.And: lambda x: all(x),
    ast.Or: lambda x: any(x),
    # Binary operators
    ast.Add: lambda x, y: x + y,
    ast.Sub: lambda x, y: x - y,
    ast.Mult: lambda x, y: x * y,
    ast.LShift: lambda x, y: x << y,
    ast.RShift: lambda x, y: x >> y,
    ast.BitOr: lambda x, y: x | y,
    ast.BitXor: lambda x, y: x ^ y,
    ast.BitAnd: lambda x, y: x & y,
    # Unary operators
    ast.Invert: lambda x: ~x,
    ast.Not: lambda x: not x,
    ast.UAdd: lambda x: +x,
    ast.USub: lambda x: -x,
    # Comparison operators
    ast.Eq: lambda x, y: x == y,
    ast.NotEq: lambda x, y: x != y,
    ast.Lt: lambda x, y: x < y,
    ast.LtE: lambda x, y: x <= y,
    ast.Gt: lambda x, y: x > y,
    ast.GtE: lambda x, y: x >= y,
}


def ast_eval_func(op: ast.AST) -> Callable[..., Any]:
    """Get the evaluation function for an AST operator."""
    op_type = type(op)
    assert op_type in _ast_eval_func_map
    return _ast_eval_func_map[op_type]
