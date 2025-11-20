# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Checks for test cases.
"""

import difflib
import os

from comopy import HDLStage, IRStage, JobPipeline, TranslatorStage

# Paths
_tests_out = "comopy/tests_out"
_tests_ref = "comopy/tests_ref"


def diff_files(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        diff = difflib.unified_diff(
            f1.readlines(),
            f2.readlines(),
            fromfile="reference",
            tofile="output",
        )
        return "".join(diff)


def check_verilog(ModuleClass, ex_prefix, project_path):
    pipeline = JobPipeline(HDLStage(), IRStage(), TranslatorStage())
    module = ModuleClass(name=f"{ex_prefix}_{ModuleClass.__name__}")
    pipeline(module)

    sv = module.translator.emit()
    sv_file = f"{module.name}.sv"
    out_file = f"{project_path}/{_tests_out}/{sv_file}"
    ref_file = f"{project_path}/{_tests_ref}/{sv_file}"
    with open(out_file, "w") as f:
        f.write(sv)
        f.write("\n")

    if os.path.exists(ref_file):
        diff = diff_files(ref_file, out_file)
        if diff:  # pragma: no cover
            with open(f"{out_file}.diff", "w") as f:
                f.write(diff)
        assert not diff
