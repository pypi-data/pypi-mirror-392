# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Setup translators for all HDL modules in a circuit hierarchy.
"""

from pathlib import Path

from comopy.config import get_comopy_context
from comopy.hdl import CircuitNode, RawModule
from comopy.utils import BasePass

from .verilog_translator import VerilogTranslator, get_module_dir


class SetupTranslator(BasePass):
    """A pass to setup translators for all modules in a circuit tree."""

    def __call__(self, tree: CircuitNode) -> CircuitNode:
        assert isinstance(tree, CircuitNode)
        assert tree.is_root and tree.is_assembled_module
        top_module = tree.obj
        assert isinstance(top_module, RawModule)
        if top_module.translator:
            raise RuntimeError(
                f"Translator for '{top_module.name}' has already been set up."
            )

        # Get destination directory for generated Verilog files
        context = get_comopy_context()
        config_dest_dir = context.trans_config.dest_dir
        if config_dest_dir:
            dest_dir = Path(config_dest_dir)
            if not dest_dir.is_absolute():
                raise ValueError(
                    "Configured 'dest_dir' must be an absolute path, "
                    f"got: {config_dest_dir}"
                )
            if dest_dir.exists() and not dest_dir.is_dir():
                raise ValueError(
                    "Configured 'dest_dir' exists but is not "
                    f"a directory: {config_dest_dir}"
                )
        else:
            top_dir = get_module_dir(top_module)
            dest_dir = top_dir / "build"

        # Create translator
        trans = VerilogTranslator(tree, dest_dir)
        top_module.attach_translator(trans)

        return tree
