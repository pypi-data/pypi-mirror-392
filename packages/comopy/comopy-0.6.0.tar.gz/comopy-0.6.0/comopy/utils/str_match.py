# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Utilities for string matching.
"""


def match_lines(actual: str, expected: str) -> bool:
    """Check if two strings match line by line."""
    if not expected:
        return True

    actual_lines = actual.splitlines()
    expected_lines = expected.splitlines()

    # Find the first matching line
    start = -1
    for i, line in enumerate(actual_lines):
        if line == expected_lines[0]:
            start = i
            break
    if start == -1:
        raise ValueError(
            "Mismatch at line 1 of expected string:\n"
            f"-Expected: {expected_lines[0]!r}\n"
            f"-Actual  :\n{actual}\n"
        )

    # Match line by line from the start position
    for i, line in enumerate(expected_lines):
        actual_idx = start + i
        if actual_idx >= len(actual_lines):
            raise ValueError(
                "Actual string has fewer lines than expected.\n"
                f"-Missing line: {line!r}\n"
                f"-Actual:\n{actual}\n"
            )
        if actual_lines[actual_idx] != line:
            raise ValueError(
                f"Mismatch at line {i} of expected string:\n"
                f"-Expected: {line!r}\n"
                f"-Actual  : {actual_lines[actual_idx]!r}\n"
                f"-Actual  :\n{actual}\n"
            )
    return True
