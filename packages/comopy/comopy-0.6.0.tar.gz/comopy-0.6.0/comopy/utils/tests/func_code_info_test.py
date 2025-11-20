# Tests for FuncCodeInfo
#

import ast

from comopy.utils.func_code_info import FuncCodeInfo


def test_FuncCodeInfo():
    def inner():  # pragma: no cover
        a = 1
        b = 2
        return a + b

    info = FuncCodeInfo(test_FuncCodeInfo)
    assert info.func == test_FuncCodeInfo
    assert __file__.endswith(info.file_path)
    assert info.lineno == 9
    assert info.code_lines[0] == "def test_FuncCodeInfo():"
    assert info.code_lines[1] == "    def inner():  # pragma: no cover"
    assert not info.ast_root

    info = FuncCodeInfo(inner)
    assert info.func == inner
    assert __file__.endswith(info.file_path)
    assert info.lineno == 10
    assert info.code_lines[0] == "def inner():  # pragma: no cover"
    assert info.code_lines[1] == "    a = 1"
    assert not info.ast_root
    assert info.parse_ast()
    assert isinstance(info.ast_root, ast.Module)
