# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Error exceptions.
"""

import ast
import inspect
import os
from typing import Optional

from .func_code_info import CodePosition, FuncCodeInfo


def _code_pos_str(
    path_str: str,
    lineno: int,
    func_name: str,
    code_line: str,
    col_offset: int = 0,
    col_width: int = 0,
) -> str:
    pos = (
        f"> File '{path_str}', line {lineno}, in {func_name}()\n"
        f"> {code_line}\n"
    )
    if col_width:
        pos += f"> {' ' * col_offset}{'^' * col_width}\n"
    return pos


class BitsAssignError(TypeError):
    """Raised for invalid assignments to Bits objects."""

    def __init__(self, nbits: int, message: str):
        assert not message.endswith(".")
        super().__init__(f"Cannot assign to Bits{nbits}: {message}.")


class BitsWidthError(ValueError):
    """Raised when bit widths mismatch in an operation."""

    def __init__(self, n_lhs: int, n_rhs: int, op_name: str):
        super().__init__(
            f"Width mismatch for {op_name}: "
            f"LHS Bits{n_lhs}, RHS Bits{n_rhs}."
            "\n- Use .ext(width), .S.ext(width), "
            "or slice [:width] to match widths."
        )


class HDLAssemblyError(Exception):
    """Raised for errors during HDL object assembly."""

    def __init__(self, message: str, pos: str = ""):
        super().__init__()
        self.message = message
        self.pos = pos

    def attach_frame_info(self, frame: Optional[inspect.FrameInfo]):
        if not frame:
            return
        assert not self.pos
        index = frame.index if frame.index else 0
        if frame.code_context:
            code_line = frame.code_context[index].rstrip()
        else:
            code_line = "(code not available)"
        self.pos = _code_pos_str(
            os.path.relpath(frame.filename),
            frame.lineno,
            frame.function,
            code_line,
        )

    def __str__(self):
        return f"\n{self.pos}HDL error: {self.message}"


class HDLSyntaxError(Exception):
    """
    Raised for syntax errors during HDL-to-IR conversion.

    Initially holds the AST node for error location; can be updated with
    precise code position info and re-raised without the node.
    """

    def __init__(self, node: Optional[ast.AST], message: str, pos=""):
        super().__init__()
        self.node = node
        self.message = message
        self.pos = pos

    def attach_code_info(self, info: FuncCodeInfo, node: ast.AST):
        assert self.node and not self.pos
        # Ignore type hints for AST
        lineno = info.lineno + node.lineno - 1  # type: ignore
        code_line = info.code_lines[node.lineno - 1]  # type: ignore
        col_offset = node.col_offset  # type: ignore
        assert node.end_col_offset  # type: ignore
        col_width = node.end_col_offset - node.col_offset  # type: ignore
        self.pos = _code_pos_str(
            info.get_file_path_str(),
            lineno,
            info.func.__name__,
            code_line,
            col_offset,
            col_width,
        )
        self.node = None

    def attach_code_pos(self, code_pos: CodePosition):
        assert not self.node and not self.pos
        assert isinstance(code_pos, CodePosition)
        info = code_pos.func_info
        lineno = code_pos.lineno
        code_line = info.code_lines[lineno - 1]
        lineno = info.lineno + lineno - 1
        self.pos = _code_pos_str(
            info.get_file_path_str(),
            lineno,
            info.func.__name__,
            code_line,
        )

    def __str__(self):
        return f"\n{self.pos}HDL error: {self.message}"
