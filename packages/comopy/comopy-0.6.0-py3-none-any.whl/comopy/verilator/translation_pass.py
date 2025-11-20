# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang
#         Shixuan Chen

"""
Translate HDL circuit tree to SystemVerilog files."
"""

from comopy.hdl import CircuitNode, RawModule
from comopy.translator import BaseTranslator
from comopy.utils import BasePass


class TranslationPass(BasePass):
    def __call__(self, tree: CircuitNode) -> CircuitNode:
        assert isinstance(tree, CircuitNode)
        assert tree.is_root and tree.is_assembled_module
        top_module = tree.obj
        assert isinstance(top_module, RawModule)

        translator = top_module.translator
        assert isinstance(translator, BaseTranslator)
        assert translator.target_language == "SystemVerilog"
        translator.emit_to_file()

        return tree
