# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Assemble HDL objects into a circuit tree.
"""

import ast
import inspect
from typing import Any, Callable, Optional, Sequence

from comopy.datatypes import ParamConst
from comopy.utils import BasePass, CodePosition, FuncCodeInfo, HDLAssemblyError

from .circuit_node import CircuitNode, Connection, ModuleInst
from .circuit_object import CircuitObject
from .parameter import LocalParam, ModuleParam
from .raw_module import RawModule, _hdl_internal_builder


# Prevent overwriting attributes of assembled circuit objects.
# For example, disallow accidental assignments like `module.in1 = 0b1010`
# which may be a typo for `module.in1 /= 0b1010`.
def __setattr_after_assemble__(obj, name: str, value: Any):
    assert isinstance(obj, CircuitObject)
    if hasattr(obj, name):
        old = getattr(obj, name)
        # TODO ModuleParam, LocalParam
        if not isinstance(old, (CircuitObject, LocalParam, ModuleParam)):
            super(CircuitObject, obj).__setattr__(name, value)
            return
        if obj._assembled:
            if isinstance(old, (LocalParam, ModuleParam)):
                raise HDLAssemblyError(
                    f"Cannot overwrite parameter '{name}' after assembling."
                )
            assert isinstance(old, CircuitObject)
            if value is not old:  # except for @=, /=, <<=
                raise HDLAssemblyError(
                    f"Cannot overwrite circuit object '{name}' "
                    "after assembling."
                )
    super(CircuitObject, obj).__setattr__(name, value)


class AssembleHDL(BasePass):
    """A pass that assembles HDL objects into a circuit tree."""

    _assemble_stack: list[CircuitNode] = []

    def __call__(self, top: CircuitObject, prev_output=None) -> CircuitNode:
        assert isinstance(top, CircuitObject)
        assert prev_output is None
        if top.assembled:
            e = HDLAssemblyError(
                f"'{top}' has already been assembled."
                f"\n- Cannot assemble the top module from an assembled object."
            )
            e.attach_frame_info(inspect.stack()[1])
            raise e

        return self.__assemble(top)

    def __assemble(self, top: CircuitObject) -> CircuitNode:
        # TODO import Package

        def __setattr_for_assemble__(
            obj: CircuitObject, name: str, value: Any
        ):
            assert isinstance(obj, CircuitObject)

            # Check child object
            if hasattr(obj, name):
                old = getattr(obj, name)
                if isinstance(old, ModuleParam):
                    # Module instantiation overwrites class ModuleParam
                    # with an instance ModuleParam. Otherwise, it is an error.
                    if not isinstance(value, ModuleParam):
                        assert isinstance(obj, RawModule)
                        assert old.param_name
                        assert old.param_name in obj.param_names
                        raise HDLAssemblyError(
                            f"Cannot overwrite module parameter '{name}'."
                        )
                if callable(old):
                    raise HDLAssemblyError(
                        f"Cannot overwrite callable attribute '{name}'."
                    )
                if not isinstance(old, CircuitObject):
                    # Overwrite non-CircuitObject
                    super(CircuitObject, obj).__setattr__(name, value)
                    return
                if value is old:
                    # Assignment for @=
                    super(CircuitObject, obj).__setattr__(name, value)
                    return
                if hasattr(obj.__class__, name):
                    # PackedStruct overwrites its class attributes
                    cls_obj = getattr(obj.__class__, name)
                    assert value is not cls_obj
                else:
                    raise HDLAssemblyError(
                        f"Cannot overwrite attribute '{name}'."
                        f"\n- Calling one builder in another builder?"
                    )

            # Check value object
            if isinstance(obj, RawModule):
                if type(value) is ParamConst:
                    # Create a local parameter from an expression
                    if not value.is_expr:
                        raise HDLAssemblyError(
                            "Cannot create ParamConst attributes in a module."
                            "\n- Use LocalParam() for local parameters."
                        )
                    value = LocalParam(value)
                elif isinstance(value, ModuleParam):
                    # Assign from a module parameter
                    assert value.param_name
                    assert value.param_name in obj.param_names
                    value = LocalParam(value)
                elif isinstance(value, LocalParam) and value.assembled:
                    # Assign from an assembled local parameter
                    value = LocalParam(value)
            if not isinstance(value, CircuitObject):
                super(CircuitObject, obj).__setattr__(name, value)
                return
            if value.assembled:
                raise HDLAssemblyError(
                    f"'{value}' has already been assembled."
                    "\n- Creating an alias for a circuit object?"
                )

            owner = assembler.__get_last_node()
            assembler.__assemble_node(value, name, owner)
            super(CircuitObject, obj).__setattr__(name, value)
            if isinstance(value, RawModule):
                assert isinstance(owner.obj, RawModule)
                owner.obj.connect_submodule(value)
                inst = ModuleInst(value)
                owner.register_submodule(inst)
            # TODO Package

        AssembleHDL._assemble_stack.clear()
        # Hook CircuitObject.__setattr__ to collect sub-objects.
        # Pass assembler to hooked __setattr__ in the closure.
        assembler = self
        CircuitObject.__setattr__ = __setattr_for_assemble__  # type: ignore

        try:
            tree = self.__assemble_node(top, top.name)
        except Exception as e:
            # delete __setattr__ before re-raising
            del CircuitObject.__setattr__
            if not isinstance(e, HDLAssemblyError):
                e = HDLAssemblyError(f"{e}")
            e.attach_frame_info(self.__get_builder_frame_from_trace())
            AssembleHDL._assemble_stack.clear()
            raise e

        CircuitObject.__setattr__ = __setattr_after_assemble__  # type: ignore
        assert not AssembleHDL._assemble_stack
        return tree

    def __assemble_node(
        self,
        obj: CircuitObject,
        name: str,
        owner: Optional[CircuitNode] = None,
    ) -> CircuitNode:
        obj._name = name
        node = CircuitNode(obj)
        if not owner:
            # Root node
            node._top = node
        else:
            owner.append_element(node)
            # Get code position for submodule instances
            node._code_pos = None
            if isinstance(obj, RawModule):
                builder_frame = self.__get_builder_frame_from_stack()
                assert isinstance(builder_frame, inspect.FrameInfo)
                info = owner.get_builder_frame_info(builder_frame)
                assert isinstance(info, FuncCodeInfo)
                lineno = builder_frame.lineno - info.lineno + 1
                node._code_pos = CodePosition(info, lineno)

        AssembleHDL._assemble_stack.append(node)
        obj._assemble()
        AssembleHDL._assemble_stack.pop()

        # Behavioral blocks
        if node.is_assembled_module:
            node.init_behavior_blocks()

        return node

    @classmethod
    def __get_builder_frame_from_trace(cls) -> Optional[inspect.FrameInfo]:
        builder_names = cls.__get_last_module_builders()
        if not builder_names:
            return None
        trace_frames = inspect.trace()
        info = None
        for frame_info in reversed(trace_frames):
            if frame_info.function in builder_names:
                info = frame_info
                break
        return info

    @classmethod
    def __get_last_module_builders(cls) -> Sequence[str]:
        module_node = cls.__get_last_node()
        # TODO Package
        if isinstance(module_node.obj, RawModule):
            return module_node.obj.get_builder_names()
        return []

    @classmethod
    def __get_last_node(cls) -> CircuitNode:
        assert cls._assemble_stack
        return cls._assemble_stack[-1]

    @classmethod
    def is_assembling(cls) -> bool:
        return bool(cls._assemble_stack)

    @classmethod
    def assemble_connection(cls):
        """Convert a continuous assignment (@=) of two connectable parts into
        a connection block, which is a function that performs blocking
        assignment (/=) for this connection during the simulation."""
        # Get call site frame, a builder of the last module
        builder_frame = cls.__get_builder_frame_from_stack(with_internal=True)
        assert isinstance(builder_frame, inspect.FrameInfo)
        # Get builder function info
        owner = cls.__get_last_node()
        info = owner.get_builder_frame_info(builder_frame)
        assert isinstance(info, FuncCodeInfo)
        # Get the assignment statement
        assert isinstance(info.ast_root, ast.Module)
        offset = builder_frame.lineno - info.lineno
        line = info.code_lines[offset]
        if line.count("@=") > 1:
            raise HDLAssemblyError(
                "Only one '@=' assignment per line is allowed."
            )
        assign = cls.__get_assign_statement(info.ast_root, offset + 1)
        if not assign:
            raise HDLAssemblyError(
                "'@=' is only supported in builder methods tagged with @build."
            )
        assert isinstance(assign, ast.AugAssign)
        # Create a connection block
        connect_func = cls.__create_conn_func(builder_frame, assign)
        target_id = ast.unparse(assign.target)
        lineno = -1
        internal = info.func.__name__ == _hdl_internal_builder
        if internal:
            # Get outer builder info for code position
            outer_frame = cls.__get_builder_frame_from_stack()
            info = owner.get_builder_frame_info(outer_frame)
            lineno = outer_frame.lineno - info.lineno + 1
        conn = Connection(
            func=connect_func,
            builder_name=info.func.__qualname__,
            assign_ast=assign,
            target_id=target_id,
            internal=internal,
            lineno=lineno,
        )
        owner.register_connection(conn)

    @classmethod
    def __get_builder_frame_from_stack(
        cls, with_internal: bool = False
    ) -> inspect.FrameInfo:
        builder_names = set(cls.__get_last_module_builders())
        assert builder_names
        if with_internal:
            builder_names.add(_hdl_internal_builder)
        stack = inspect.stack()
        info = None
        for frame_info in stack:
            if frame_info.function in builder_names:
                info = frame_info
                break
        assert info
        return info

    @classmethod
    def __get_assign_statement(
        cls, root: ast.AST, line_offset: int
    ) -> Optional[ast.AugAssign]:
        for node in ast.walk(root):
            if isinstance(node, ast.AugAssign) and node.lineno == line_offset:
                assert isinstance(node.op, ast.MatMult)
                return node
        return None

    @classmethod
    def __create_conn_func(
        cls,
        builder_frame: inspect.FrameInfo,
        assign: ast.AugAssign,
    ) -> Callable:
        code = ast.unparse(assign).replace("@=", "/=")
        # NOTE: Potential reference cycle between closure and frame context.
        # Python's cycle GC can handle this in most cases.
        builder_globals = builder_frame.frame.f_globals
        builder_locals = builder_frame.frame.f_locals

        def _connect_func():
            exec(code, builder_globals, builder_locals)

        return _connect_func
