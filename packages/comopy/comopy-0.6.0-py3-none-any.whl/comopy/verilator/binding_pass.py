# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang
#         Shixuan Chen

"""
Generate Python bindings for Verilated modules.
"""

import jinja2

from comopy.hdl import CircuitNode, RawModule, Wire
from comopy.translator import BaseTranslator
from comopy.utils import BasePass


def _width_to_vtype(nbits: int) -> str:
    assert nbits > 0
    assert nbits <= 64  # TODO >=64-bit need getter/setter methods
    if nbits <= 8:
        return "CData"
    elif nbits <= 16:
        return "SData"
    elif nbits <= 32:
        return "IData"
    elif nbits <= 64:
        return "QData"
    return "UnknownType"


class BindingPass(BasePass):

    jinja_files = {"vsim": "vsimulator_binding.jinja"}
    templates: dict[str, jinja2.Template]

    top_inputs: list[tuple[str, str]]  # list of (port_name, port_type)
    top_outputs: list[tuple[str, str]]  # list of (port_name, port_type)

    def __init__(self):
        super().__init__()
        self.templates = {}
        env = jinja2.Environment(
            loader=jinja2.PackageLoader("comopy.verilator", "templates"),
            autoescape=False,  # No escaping for C++ code generation
            keep_trailing_newline=True,
        )
        for name, filename in self.jinja_files.items():
            template = env.get_template(filename)
            self.templates[name] = template

    def __call__(self, tree: CircuitNode) -> CircuitNode:
        assert isinstance(tree, CircuitNode)
        assert tree.is_root and tree.is_assembled_module
        top_module = tree.obj
        assert isinstance(top_module, RawModule)
        translator = top_module.translator
        assert isinstance(translator, BaseTranslator)

        # Generate binding code
        self.__collect_top_ports(top_module)
        code = self.__emit_top_binding(top_module)

        # Write to translator's destination directory
        dest_dir = translator.dest_path.parent
        module_name = type(top_module).__name__
        binding_file = dest_dir / f"V{module_name}_binding.cpp"
        binding_file.write_text(code, encoding="utf-8")

        return tree

    def __collect_top_ports(self, top_module: RawModule):
        self.top_inputs = []
        self.top_outputs = []
        for port in top_module.all_ports:
            assert isinstance(port, Wire)
            assert not port.is_inout_port
            nbits = port.nbits
            if port.is_input_port:
                self.top_inputs.append((port.name, _width_to_vtype(nbits)))
            elif port.is_output_port:
                self.top_outputs.append((port.name, _width_to_vtype(nbits)))

    def __emit_top_binding(self, top_module: RawModule) -> str:
        module_name = type(top_module).__name__
        code = self.templates["vsim"].render(
            module_name=module_name,
            top_inputs=self.top_inputs,
            top_outputs=self.top_outputs,
        )
        return code
