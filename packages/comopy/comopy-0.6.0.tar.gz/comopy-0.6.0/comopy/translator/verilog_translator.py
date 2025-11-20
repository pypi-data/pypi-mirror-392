# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Translator for SystemVerilog code generation.
"""

import inspect
import io
from pathlib import Path

import circt
import circt.ir as IR

from comopy.hdl import CircuitNode, RawModule
from comopy.translator.base_translator import BaseTranslator


def get_module_dir(module: RawModule) -> Path:
    """Get the directory containing the module class file."""
    assert isinstance(module, RawModule)
    module_class = type(module)
    module_file = inspect.getfile(module_class)
    return Path(module_file).parent


class VerilogTranslator(BaseTranslator):

    _module_node: CircuitNode
    _ir_top: IR.Module
    _dest_path: Path

    def __init__(self, module_node: CircuitNode, dest_dir: Path | None = None):
        assert isinstance(module_node, CircuitNode)
        assert module_node.is_root and module_node.is_assembled_module
        self._module_node = module_node
        self._ir_top = module_node.ir_top
        assert isinstance(self._ir_top, IR.Module)

        module_obj = module_node.obj
        assert isinstance(module_obj, RawModule)
        if dest_dir is None:
            dest_dir = get_module_dir(module_obj)
        assert isinstance(dest_dir, Path)
        module_class = type(module_obj)
        self._dest_path = dest_dir / f"{module_class.__name__}.sv"

    @property
    def target_language(self) -> str:
        """Get the name of the target language."""
        return "SystemVerilog"

    @property
    def file_extension(self) -> str:
        """Get the file extension for the target language."""
        return ".sv"

    @property
    def dest_path(self) -> Path:
        """Get the destination file path."""
        return self._dest_path

    def emit(self) -> str:
        """Emit the bound IR module as target language code."""
        with self._ir_top.context:
            return self.__export_verilog()

    def __export_verilog(self) -> str:
        op = self._ir_top.operation
        op.attributes["circt.loweringOptions"] = IR.StringAttr.get(
            "omitVersionComment, emitWireInPorts"
        )

        with io.StringIO() as buffer:
            circt.export_verilog(self._ir_top, buffer)
            sv_code = buffer.getvalue().rstrip("\n")

        return sv_code
