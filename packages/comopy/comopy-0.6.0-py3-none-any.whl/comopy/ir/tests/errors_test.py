# Tests for error messages
#

import difflib
import os
import re
import sys

from .function_parser_test import print_FunctionParser_errors
from .object_parser_test import print_ObjectParser_errors
from .structure_pass_test import print_StructurePass_errors

# Paths
_tests_out = "comopy/tests_out"
_tests_ref = "comopy/tests_ref"
_msg_file = "hdl_syntax_errors.txt"


def diff_files(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        lines1 = [_normalize_path(line) for line in f1.readlines()]
        lines2 = [_normalize_path(line) for line in f2.readlines()]
        diff = difflib.unified_diff(
            lines1,
            lines2,
            fromfile="reference",
            tofile="output",
        )
        return "".join(diff)


def _normalize_path(line):
    # 'XXXX/comopy/ir/xxxx' -> '.../comopy/ir/xxxx'
    pattern = r"(> File ').*?(comopy/ir/[^']+)"
    if re.search(pattern, line):
        return re.sub(pattern, r"\1.../\2", line)
    return line


def test_HDLSyntaxError_messages(project_path):
    out_file = f"{project_path}/{_tests_out}/{_msg_file}"
    ref_file = f"{project_path}/{_tests_ref}/{_msg_file}"

    with open(out_file, "w") as f:
        sys.stdout = f
        print("\n==== StructurePass ====")
        print_StructurePass_errors()
        print("\n==== FunctionParser ====")
        print_FunctionParser_errors()
        print("\n==== ObjectParser ====")
        print_ObjectParser_errors()
        sys.stdout = sys.__stdout__

    if os.path.exists(ref_file):
        diff = diff_files(ref_file, out_file)
        if diff:  # pragma: no cover
            with open(f"{out_file}.diff", "w") as f:
                f.write(diff)
        assert not diff
