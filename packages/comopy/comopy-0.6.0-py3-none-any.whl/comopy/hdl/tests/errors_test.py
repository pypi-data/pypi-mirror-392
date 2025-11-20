# Tests for error messages
#

import difflib
import os
import re
import sys

from .assemble_hdl_test import print_AssembleHDL_errors
from .connectable_test import print_Connectable_errors
from .io_struct_test import print_IOStruct_errors
from .module_test import print_Module_errors
from .raw_module_test import print_RawModule_errors

# Paths
_tests_out = "comopy/tests_out"
_tests_ref = "comopy/tests_ref"
_msg_file = "hdl_assembly_errors.txt"


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
    # 'XXXX/comopy/hdl/xxxx' -> '.../comopy/hdl/xxxx'
    pattern = r"(> File ').*?(comopy/hdl/[^']+)"
    if re.search(pattern, line):
        return re.sub(pattern, r"\1.../\2", line)
    return line


def test_HDLAssembleError_messages(project_path):
    out_file = f"{project_path}/{_tests_out}/{_msg_file}"
    ref_file = f"{project_path}/{_tests_ref}/{_msg_file}"

    with open(out_file, "w") as f:
        sys.stdout = f
        print("\n==== AssembleHDL ====")
        print_AssembleHDL_errors()
        print("\n==== Module ====")
        print_RawModule_errors()
        print_Module_errors()
        print("\n==== Connectable ====")
        print_Connectable_errors()
        print("\n==== I/O structure ====")
        print_IOStruct_errors()
        sys.stdout = sys.__stdout__

    if os.path.exists(ref_file):
        diff = diff_files(ref_file, out_file)
        if diff:  # pragma: no cover
            with open(f"{out_file}.diff", "w") as f:
                f.write(diff)
        assert not diff
