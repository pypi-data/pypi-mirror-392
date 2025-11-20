# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Code information for a Python function.
"""

import ast
import inspect
import os
import re
from types import FunctionType
from typing import Callable, NamedTuple, Optional

# Compiled regular expressions
_re_space = re.compile(r"^( *?)(@|def)")  # Leading spaces before @|def


class FuncCodeInfo:
    """Code information for a Python function."""

    func: Callable
    file_path: str
    lineno: int
    code_lines: list[str]
    ast_root: Optional[ast.Module]

    def __init__(self, func: Callable):
        super().__init__()
        assert type(func) is FunctionType
        self.func = func
        file_path = inspect.getsourcefile(func)
        assert file_path
        self.file_path = file_path
        lines, self.lineno = inspect.getsourcelines(func)
        indent = self.__get_indent(lines)
        # remove trailing "\n" and the first level indent
        self.code_lines = [s.rstrip()[indent:] for s in lines]
        self.ast_root = None

    def __get_indent(self, lines) -> int:
        indent = 0
        for line in lines:
            # Leading spaces of top-level @|def
            if match := _re_space.match(line):
                indent = len(match.group(1))
                break
        return indent

    def parse_ast(self) -> ast.Module:
        assert self.ast_root is None
        assert self.code_lines
        code = "\n".join(self.code_lines)
        self.ast_root = ast.parse(code)
        return self.ast_root

    def get_file_path_str(self) -> str:
        return os.path.relpath(self.file_path)


class CodePosition(NamedTuple):
    func_info: FuncCodeInfo
    lineno: int
