# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Generate structural IR entities from a circuit tree.
"""

from typing import Any, Callable

import circt
import circt.ir as IR
from circt.dialects import hw, sv
from circt.support import BackedgeBuilder, connect

import comopy.hdl as HDL
from comopy.config import IRConfig, get_comopy_context
from comopy.utils import BasePass, CodePosition, FuncCodeInfo, HDLSyntaxError

from .circt_ir import *
from .object_parser import ObjectParser
from .parser_defs import *

# Handlers for HDL object types
_hdl_handlers: dict[type, Callable] = {}


# Decorator for HDL type handlers
def handler(Type: type[HDL.CircuitObject]) -> Callable:
    def _handler(func):
        assert issubclass(Type, HDL.CircuitObject)
        assert Type not in _hdl_handlers
        _hdl_handlers[Type] = func
        return func

    return _handler


class StructurePass(BasePass):
    """A pass to generate structural IR entities from a circuit tree."""

    # Configuration
    config: IRConfig

    # Cache for all hw.HWModuleOp operations in current MLIR module
    hw_module_cache: dict[type[HDL.RawModule], hw.HWModuleOp]

    # Current module information
    module_node: HDL.CircuitNode
    module_symbols: dict[str, Any]  # name -> IR entity
    obj_parser: ObjectParser

    def __call__(self, tree: HDL.CircuitNode) -> HDL.CircuitNode:
        assert isinstance(tree, HDL.CircuitNode)
        assert tree.is_root and tree.is_assembled_module
        top_obj = tree.obj
        assert isinstance(top_obj, HDL.RawModule)
        top_cls = type(top_obj).__name__
        if top_obj.ir:
            raise RuntimeError(
                f"IR has already been generated for {top_cls}({top_obj.name})."
            )
        assert tree.ir_top is None

        self.config = get_comopy_context().ir_config
        self.hw_module_cache = {}
        with IR.Context() as ctx, IR.Location.unknown(), BackedgeBuilder():
            circt.register_dialects(ctx)

            # MLIR module, the root container for all IR entities
            mlir_module = IR.Module.create()
            tree.attach_ir_top(mlir_module)
            with IR.InsertionPoint(mlir_module.body):
                # All modules in the depth-first order (define-before-use)
                for node in tree.iter_postorder():
                    if not node.is_assembled_module:
                        continue
                    assert isinstance(node.obj, HDL.RawModule)
                    module_type = type(node.obj)
                    if module_type not in self.hw_module_cache:
                        hw_module = self.generate_module(node)
                        assert isinstance(hw_module, hw.HWModuleOp)
                        self.hw_module_cache[module_type] = hw_module
        return tree

    def generate_module(self, module_node: HDL.CircuitNode) -> hw.HWModuleOp:
        module_obj = module_node.obj
        assert isinstance(module_obj, HDL.RawModule)

        # Create a hw.HWModuleOp operation for the HDL module
        hw_module = hw.HWModuleOp(name=module_obj.__class__.__name__)
        module_obj.attach_ir(hw_module)
        ports = self.__get_all_ports(module_obj)
        module_ports = []
        for port_name, port_type, port_dir in ports:
            name = IR.StringAttr.get(str(port_name))
            port = hw.ModulePort(name, port_type, port_dir)
            module_ports.append(port)
        hw_module_type = hw.ModuleType.get(module_ports)
        hw_module.attributes["module_type"] = IR.TypeAttr.get(hw_module_type)

        # Set up current module information
        self.module_node = module_node
        self.module_symbols = {}
        self.obj_parser = ObjectParser(module_node, self.module_symbols)

        # Create hw.HWModuleOp body
        entry_block = hw_module.add_entry_block()
        with IR.InsertionPoint(entry_block):
            # In CIRCT, output ports are BlockArguments and are driven
            # by hw.OutputOp.
            # Create an auto var sv.LogicOp for each output port for later use.
            output_comment = sv.verbatim(COMMENT_OUTPUT_VARS, [])
            output_vars = []
            for port_name, port_type, port_dir in ports:
                if port_dir != hw.ModulePortDirection.OUTPUT:
                    continue
                var_name = auto_module_output(port_name)
                io_type = hw.InOutType.get(port_type)
                var_op = sv.LogicOp(io_type, var_name)
                output_vars.append(var_op)
                self.add_symbol(var_name, var_op)
            if output_vars:
                ir_sv_newline()
            else:
                output_comment.erase()

            # Create placeholder for local parameters
            sv.verbatim(COMMENT_LOCALPARAMS, [])
            sv.verbatim(COMMENT_LOCALPARAMS_END, [])

            # Generate IR for all module elements
            for elem in module_node.elements:
                ir_op = self.__generate_element_ir(elem)
                self.add_symbol(elem.name, ir_op)

            # Read values from the output vars and pass them to hw.OutputOp.
            ir_force_sv_newline()  # Mark the end of the module body
            output_values = []
            for var in output_vars:
                output_values.append(sv.read_inout(var))
            hw.OutputOp(output_values)

        return hw_module

    def __get_all_ports(
        self, module_obj: HDL.RawModule
    ) -> list[tuple[str, IR.Type, hw.ModulePortDirection]]:
        ports = []
        for port in module_obj.all_ports:
            assert isinstance(port, HDL.Wire) and port.is_port
            if port.is_input_port:
                port_type = ir_integer_type(port.nbits)
                port_dir = hw.ModulePortDirection.INPUT
                ports.append((port.name, port_type, port_dir))
            elif port.is_output_port:
                port_type = ir_integer_type(port.nbits)
                port_dir = hw.ModulePortDirection.OUTPUT
                ports.append((port.name, port_type, port_dir))
            else:
                assert port.is_inout_port
                assert False, "UNIMPLEMENTED"
        return ports

    def __generate_element_ir(self, node: HDL.CircuitNode) -> Any:
        for Type, func in _hdl_handlers.items():
            if isinstance(node.obj, Type):
                return func(self, node)
        raise HDLSyntaxError(
            None,
            f"Unsupported HDL object type '{node.obj.__class__.__name__}'.",
        )

    # Symbol table
    #
    def add_symbol(self, name: str, ir: Any):
        assert name not in self.module_symbols
        assert ir is not None
        self.module_symbols[name] = ir

    def get_symbol(self, name: str) -> Any:
        assert name in self.module_symbols
        return self.module_symbols[name]

    # Handlers for module structural elements
    #
    @handler(HDL.Logic)
    def handle_Logic(self, node: HDL.CircuitNode) -> sv.LogicOp:
        logic = node.obj
        assert isinstance(logic, HDL.Logic)
        logic_type = hw.InOutType.get(ir_integer_type(logic.nbits))
        return sv.LogicOp(logic_type, logic.name)

    @handler(HDL.Wire)
    def handle_Wire(
        self, node: HDL.CircuitNode
    ) -> IR.BlockArgument | sv.LogicOp:
        if node.owner is self.module_node and node.obj.is_port:
            port = node.obj
            assert isinstance(port, HDL.Wire)
            assert not port.is_inout_port, "UNIMPLEMENTED"
            if port.is_input_port:
                module_obj = self.module_node.obj
                assert isinstance(module_obj, HDL.RawModule)
                module_ir = module_obj.ir
                port_ir = ir_get_module_input(module_ir, port.name)
                assert isinstance(port_ir, IR.BlockArgument)
                return port_ir
            if port.is_output_port:
                var_name = auto_module_output(port.name)
                port_ir = self.get_symbol(var_name)
                assert isinstance(port_ir, sv.LogicOp)
                return port_ir
        assert False, "UNIMPLEMENTED"

    @handler(HDL.SignalArray)
    def handle_Array(self, node: HDL.CircuitNode) -> sv.LogicOp:
        array = node.obj
        assert isinstance(array, HDL.SignalArray)
        element_width = array.elem_template.nbits
        n_elements = array.size
        uarray_type = ir_unpacked_array_type(element_width, n_elements)
        inout_uarray_type = hw.InOutType.get(uarray_type)
        return sv.LogicOp(inout_uarray_type, array.name)

    @handler(HDL.RawModule)
    def handle_ModuleInst(self, node: HDL.CircuitNode):
        submodule = node.obj
        assert isinstance(submodule, HDL.RawModule)
        hw_submodule = self.hw_module_cache.get(type(submodule))
        assert isinstance(hw_submodule, hw.HWModuleOp)

        # Comment for the instance
        ir_sv_newline()
        if self.config.comment_instance:
            code_pos = node.code_pos
            assert isinstance(code_pos, CodePosition)
            assert isinstance(code_pos.func_info, FuncCodeInfo)
            code_line = code_pos.func_info.code_lines[code_pos.lineno - 1]
            ir_sv_comment_code([code_line])

        # No port connections, instantiate the submodule directly
        if not (port_conns := submodule.port_conns):
            inst_builder = hw_submodule.instantiate(submodule.name)
            inst_ir = inst_builder.opview
            ir_sv_newline()
            return inst_ir

        # Prepare input port connections
        ports = submodule.all_ports
        assert len(ports) == len(port_conns)
        input_conns: list[tuple[str, Any]] = []
        for port, conn in zip(ports, port_conns):
            assert isinstance(port, HDL.Wire) and port.is_port
            assert not port.is_inout_port, "UNIMPLEMENTED"
            if port.is_input_port:
                if conn is None:  # Don't use `if conn`, const 0 is also valid
                    # Create an auto variable for unconnected input port
                    var_name = auto_inst_input(submodule.name, port.name)
                    port_type = ir_integer_type(port.nbits)
                    io_type = hw.InOutType.get(port_type)
                    peer_ir = sv.LogicOp(io_type, var_name)
                    self.add_symbol(var_name, peer_ir)
                elif isinstance(conn, int):
                    # Assembler has checked the constant width.
                    peer_ir = ir_constant_op(port.nbits, conn)
                else:
                    _, peer_ir = self.obj_parser(conn, node.code_pos)
                input_conns.append((port.name, peer_ir))

        # Create hw.InstanceOp and connect input ports
        inst_builder = hw_submodule.instantiate(submodule.name)
        inst_ir = inst_builder.opview
        assert isinstance(inst_ir, hw.InstanceOp)
        for port_name, peer_ir in input_conns:
            input = getattr(inst_builder, port_name)
            connect(input, peer_ir)

        # Connect the results of hw.InstanceOp to the output destinations
        for port, conn in zip(ports, port_conns):
            assert isinstance(port, HDL.Wire) and port.is_port
            if port.is_output_port and conn is not None:
                _, peer_ir = self.obj_parser(conn, node.code_pos, at_lhs=True)
                output = getattr(inst_builder, port.name)
                sv.AssignOp(peer_ir, inst_ir.results[output.index])

        # Finish the instance
        ir_sv_newline()
        return inst_ir
