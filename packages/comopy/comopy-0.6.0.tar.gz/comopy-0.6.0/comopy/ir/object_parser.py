# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Analyze HDL objects and find corresponding IR entities.
"""

from contextlib import contextmanager
from functools import wraps
from typing import Any, Optional

import circt.ir as IR
from circt.dialects import hw, sv

import comopy.hdl as HDL
from comopy.datatypes import Bits, Bits1
from comopy.utils import CodePosition, HDLSyntaxError

from .circt_ir import *
from .parser_defs import *


@contextmanager
def parsing_context(code_pos: Optional[CodePosition]):
    try:
        yield
    except HDLSyntaxError as e:
        # Patch message with code position
        assert e.node is None
        if code_pos:
            e.attach_code_pos(code_pos)
        raise e


class ObjectParser:
    """Analyzes HDL objects and finds corresponding IR entities."""

    module_node: HDL.CircuitNode
    symbols: dict[str, Any]  # name -> IR entity
    code_pos: Optional[CodePosition]
    at_lhs: bool
    query_id_only: bool  # Avoid generating redundant IR entities

    def __init__(self, module_node: HDL.CircuitNode, symbols: dict[str, Any]):
        assert isinstance(module_node, HDL.CircuitNode)
        assert module_node.is_assembled_module
        assert isinstance(module_node.obj, HDL.RawModule)
        assert isinstance(module_node.obj.ir, hw.HWModuleOp)
        self.module_node = module_node
        self.symbols = symbols
        self.code_pos = None
        self.at_lhs = False
        self.query_id_only = False

    # Interface
    #
    def __call__(
        self,
        obj: Any,
        code_pos: Optional[CodePosition] = None,
        at_lhs: bool = False,
        query_id_only: bool = False,
    ) -> tuple[str, Any]:
        """Return the dependency ID and corresponding IR entity."""
        self.code_pos = code_pos
        self.at_lhs = at_lhs
        self.query_id_only = query_id_only
        match obj:
            case Bits():
                e = HDLSyntaxError(
                    None,
                    "Bits constant or expression is "
                    "not supported as a signal.",
                )
                if self.code_pos:
                    e.attach_code_pos(self.code_pos)
                raise e
            case HDL.CircuitObject():
                return self.circuit_object_ir(obj)
            case HDL.SignalSlice():
                return self.signal_slice_ir(obj)
        assert False, "UNIMPLEMENTED"

    # Symbol table
    #
    def lookup_symbol(self, name: str) -> Any:
        assert name in self.symbols
        return self.symbols[name]

    # Context
    #
    # Decorator for parsing functions, catching syntax exceptions
    @staticmethod
    def parsing(func: Callable):
        @wraps(func)
        def func_with_context(self, *args, **kwargs):
            with parsing_context(self.code_pos):
                return func(self, *args, **kwargs)

        return func_with_context

    @parsing
    def circuit_object_ir(self, obj: HDL.CircuitObject) -> tuple[str, Any]:
        assert isinstance(obj, HDL.CircuitObject)
        assert obj.assembled
        obj_node = obj.node
        assert isinstance(obj_node, HDL.CircuitNode)

        # Retrieve hierarchy from module node to object node
        all_nodes = obj_node.get_hierarchy_till(self.module_node.name)
        if not (all_nodes and all_nodes[0] is self.module_node):
            raise HDLSyntaxError(
                None,
                f"Circuit object {obj_node.full_name} is not accessible "
                "from current module.",
            )

        # Module attribute
        if len(all_nodes) == 2:
            node = all_nodes[1]
            if node.obj.is_input_port:
                if self.at_lhs:
                    raise HDLSyntaxError(
                        None,
                        f"Cannot assign to input port '{node.name}'.",
                    )
                module_obj = self.module_node.obj
                assert isinstance(module_obj, HDL.RawModule)
                ir = ir_get_module_input(module_obj.ir, node.name)
                assert isinstance(ir, IR.BlockArgument)
                return node.name, ir
            if node.obj.is_output_port:
                ir_name = auto_module_output(node.name)
            else:
                ir_name = node.name
            ir = self.lookup_symbol(ir_name)
            if isinstance(obj, HDL.RawModule):
                # Submodule instance
                assert isinstance(ir, hw.InstanceOp)
                return node.name, ir
            return node.name, ir if self.at_lhs else ir_rvalue(ir)

        # Submodule port
        container = all_nodes[1]
        if container.is_assembled_module:
            dep_id = f"{container.name}.{all_nodes[2].name}"
            return dep_id, self.__submodule_port_ir(all_nodes[1:])
        assert False, "UNIMPLEMENTED"

    def __submodule_port_ir(self, nodes: list[HDL.CircuitNode]) -> Any:
        submodule_node = nodes[0]
        submodule_ir = self.lookup_symbol(submodule_node.name)
        assert isinstance(submodule_ir, hw.InstanceOp)

        port_node = nodes[1]
        port = port_node.obj
        port_name = f"{submodule_node.name}.{port_node.name}"
        if not port.is_port:
            raise HDLSyntaxError(
                None,
                f"Circuit object {port_name} is not a port.",
            )
        assert isinstance(port, HDL.Wire) and len(nodes) == 2
        if port.is_input_port:
            if not self.at_lhs:
                raise HDLSyntaxError(
                    None,
                    f"Cannot read submodule input port {port_name}.",
                )
            if self.query_id_only:
                return None
            auto_wire = auto_inst_input(submodule_node.name, port.name)
            ir = self.lookup_symbol(auto_wire)
            assert isinstance(ir, sv.LogicOp)
            return ir
        elif port.is_output_port:
            assert not self.at_lhs  # Assembler has checked multiple drivers.
            if self.query_id_only:
                return None
            return ir_get_instance_output(submodule_ir, port.name)

    @parsing
    def signal_slice_ir(self, obj: HDL.SignalSlice) -> tuple[str, Any]:
        assert isinstance(obj, HDL.SignalSlice)

        # Owner signal
        signal = obj.owner
        assert isinstance(signal, HDL.Signal)
        id, signal_ir = self.circuit_object_ir(signal)
        if self.query_id_only:
            return id, None

        # Slice key
        if isinstance(obj.key, slice):
            if obj.key.stop is None:
                key = slice(obj.key.start, signal.nbits, obj.key.step)
            else:
                key = obj.key
            return id, self.__slice_ir(signal_ir, key)
        elif isinstance(obj.key, tuple):
            return id, self.__part_select_ir(signal_ir, obj.key)
        else:
            return id, self.__index_ir(signal_ir, obj.key)

    def __slice_ir(self, signal_ir: Any, key: slice) -> IR.OpResult | IR.Value:
        assert key.step is None  # Checked by the assembler.
        start = key.start if key.start is not None else 0
        if not isinstance(start, int):
            raise HDLSyntaxError(
                None, "Lower bound must be an integer constant."
            )
        stop = key.stop
        if not isinstance(stop, int):
            raise HDLSyntaxError(
                None, "Upper bound must be an integer constant."
            )
        assert 0 <= start < stop  # Checked by the assembler.
        return self.__access_slice(signal_ir, start, stop - start)

    def __part_select_ir(
        self, signal_ir: Any, key: tuple
    ) -> IR.OpResult | IR.Value:
        assert len(key) in (2, 3)  # Checked by the assembler.
        base = key[0]
        if not isinstance(base, int):
            raise HDLSyntaxError(
                None, "Part-select base must be an integer constant."
            )
        width = key[1]
        if not isinstance(width, int):
            raise HDLSyntaxError(
                None, "Part-select width must be an integer constant."
            )
        if len(key) == 3:
            dir = key[2]
            assert isinstance(dir, Bits1)  # Checked by the assembler.
            if dir == 1:
                assert width > 0  # Checked by the assembler.
                width = -width
        if width > 0:
            return self.__access_part(signal_ir, base, width, descending=False)
        else:
            return self.__access_part(signal_ir, base, -width, descending=True)

    def __index_ir(self, signal_ir: Any, index: int) -> IR.OpResult | IR.Value:
        if not isinstance(index, int):
            raise HDLSyntaxError(None, "Index must be an integer constant.")
        return self.__access_slice(signal_ir, index, 1)

    def __access_slice(
        self, signal_ir: Any, base: int, width: int
    ) -> IR.OpResult | IR.Value:
        assert isinstance(base, int)
        assert isinstance(width, int) and width > 0

        # LHS
        if self.at_lhs:
            assert isinstance(signal_ir, sv.LogicOp)
            base_ir = ir_constant_op(32, base)
            return sv.indexed_part_select_inout(signal_ir, base_ir, width)

        # RHS
        assert isinstance(signal_ir, IR.Value)
        ir_op = ir_extract_op(signal_ir, base, width)
        return ir_rvalue(ir_op)

    def __access_part(
        self, signal_ir: Any, base: int, width: int, descending: bool
    ) -> IR.OpResult:
        assert isinstance(base, int)
        assert isinstance(width, int) and width > 0
        base_ir = ir_constant_op(32, base)

        # LHS
        if self.at_lhs:
            assert isinstance(signal_ir, sv.LogicOp)
            return sv.indexed_part_select_inout(
                signal_ir, base_ir, width, decrement=descending
            )

        # RHS
        assert isinstance(signal_ir, IR.Value)
        return sv.indexed_part_select(
            signal_ir, base_ir, width, decrement=descending
        )
