# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Circuit tree assembled from HDL circuit objects.
"""

from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass, field
from enum import Enum
from types import FunctionType
from typing import Any, Callable, Optional

from comopy.utils import CodePosition, FuncCodeInfo

from .circuit_object import CircuitObject
from .raw_module import RawModule


@dataclass
class ModuleInst:
    """Module instance information."""

    module_obj: RawModule


@dataclass
class Connection:
    """Connection block for continuous assignments (@=)."""

    func: Callable
    builder_name: str  # outer builder if connecting a port
    assign_ast: ast.AugAssign
    target_id: str

    # For a port connection
    internal: bool = False
    lineno: int = -1


@dataclass
class Sensitivity:
    """Clock sensitivity information for sequential blocks."""

    # Preserve order (list, instead of set) for deterministic Verilog output
    pos_edges: list[str] = field(default_factory=list)
    neg_edges: list[str] = field(default_factory=list)


@dataclass
class Dependency:
    """Signal dependency information for behavioral blocks."""

    reads: set[str] = field(default_factory=set)
    writes: set[str] = field(default_factory=set)

    def __str__(self):
        reads = ", ".join(self.reads)
        writes = ", ".join(self.writes)
        return f"{reads} -> {writes}"


@dataclass
class Behavior:
    """Behavioral block information."""

    class Kind(Enum):
        MODULE_INST = "inst"
        CONNECTION = "conn"
        COMB_BLOCK = "comb"
        SEQ_BLOCK = "seq"

    id: str = ""
    kind: Kind = Kind.COMB_BLOCK
    func: Optional[Callable] = None
    conn: Optional[Connection] = None
    inst: Optional[ModuleInst] = None
    edges: Sensitivity = field(default_factory=Sensitivity)
    deps: Dependency = field(default_factory=Dependency)

    def __post_init__(self):
        assert self.id == ""
        match self.kind:
            case self.Kind.MODULE_INST:
                assert isinstance(self.inst, ModuleInst)
                assert isinstance(self.inst.module_obj, RawModule)
                block_name = self.inst.module_obj.name
            case self.Kind.CONNECTION:
                assert callable(self.func)
                assert isinstance(self.conn, Connection)
                assert self.func == self.conn.func
                block_name = self.conn.target_id
            case _:
                assert callable(self.func)
                block_name = self.func.__name__
        self.id = f"[{self.kind.value}]{block_name}"

    @property
    def func_name(self):
        if self.kind == self.Kind.CONNECTION:
            return self.conn.builder_name.split(".")[-1]
        return self.func.__name__

    @classmethod
    def submodule(cls, inst: ModuleInst):
        return cls(inst=inst, kind=cls.Kind.MODULE_INST)

    @classmethod
    def connection(cls, conn: Connection):
        return cls(func=conn.func, conn=conn, kind=cls.Kind.CONNECTION)

    @classmethod
    def comb_block(cls, func: Callable):
        return cls(func=func, kind=cls.Kind.COMB_BLOCK)

    @classmethod
    def seq_block(cls, func: Callable):
        return cls(func=func, kind=cls.Kind.SEQ_BLOCK)

    def set_conn_target_id(self, id: str):
        assert self.kind == self.Kind.CONNECTION
        assert isinstance(self.conn, Connection)
        self.conn.target_id = id
        self.id = f"[{self.kind.value}]{self.conn.target_id}"


class CircuitNodeBFSIterator:
    """Iterator for traversing CircuitNode in breadth-first order."""

    def __init__(self, root: CircuitNode):
        assert isinstance(root, CircuitNode)
        self._queue: list[CircuitNode] = [root]
        self._index: int = 0

    def __iter__(self):
        return self

    def __next__(self) -> CircuitNode:
        if self._index < len(self._queue):
            node = self._queue[self._index]
            self._index += 1
            self._queue.extend(node._elements)
            return node
        else:
            raise StopIteration


class CircuitNodeDFSIterator:
    """Iterator for traversing CircuitNode in depth-first order."""

    def __init__(self, root: CircuitNode):
        assert isinstance(root, CircuitNode)
        self._stack: list[CircuitNode] = [root]

    def __iter__(self):
        return self

    def __next__(self) -> CircuitNode:
        if self._stack:
            node = self._stack.pop()
            # Add elements in reverse order to maintain left-to-right traversal
            self._stack.extend(reversed(node._elements))
            return node
        else:
            raise StopIteration


class CircuitNodePostOrderIterator:
    """Iterator for traversing CircuitNode in post-order (children first)."""

    def __init__(self, root: CircuitNode):
        assert isinstance(root, CircuitNode)
        self._result: list[CircuitNode] = []
        self._index: int = 0
        self.__build_postorder(root)

    def __build_postorder(self, node: CircuitNode):
        for child in node._elements:
            self.__build_postorder(child)
        self._result.append(node)

    def __iter__(self):
        return self

    def __next__(self) -> CircuitNode:
        if self._index < len(self._result):
            node = self._result[self._index]
            self._index += 1
            return node
        else:
            raise StopIteration


class CircuitNode:
    """Circuit node built from an HDL object."""

    # Tree structure
    _obj: CircuitObject
    _ir_top: Any  # Top-level MLIR module
    _owner: Optional[CircuitNode]
    _elements: list[CircuitNode]
    _level: int
    _name: str
    _full_name: str
    _top: Optional[CircuitNode]
    _code_pos: Optional[CodePosition]

    # Behavioral blocks
    _inst_blocks: list[Behavior]
    _conn_blocks: list[Behavior]
    _comb_blocks: list[Behavior]
    _seq_blocks: list[Behavior]

    def __init__(self, obj: CircuitObject):
        assert isinstance(obj, CircuitObject)
        assert not obj.assembled
        assert obj.node is None
        self._obj = obj
        self._ir_top = None
        obj._node = self
        self._owner = None
        self._elements = []
        self._level = 0
        self._name = obj.name
        self._full_name = self._name
        self._top = None
        self._code_pos = None

        # Behavior
        self._inst_blocks = []
        self._conn_blocks = []
        self._comb_blocks = []
        self._seq_blocks = []

    def __str__(self) -> str:
        return f"Circuit({self._full_name})"

    # Properties
    #
    @property
    def obj(self) -> CircuitObject:
        return self._obj

    @property
    def ir_top(self) -> Any:
        return self._ir_top

    @property
    def owner(self) -> Optional[CircuitNode]:
        return self._owner

    @property
    def elements(self) -> tuple[CircuitNode, ...]:
        return tuple(self._elements)

    @property
    def level(self) -> int:
        return self._level

    @property
    def name(self) -> str:
        return self._name

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def top(self) -> CircuitNode:
        assert self._top
        return self._top

    @property
    def code_pos(self) -> Optional[CodePosition]:
        return self._code_pos

    @property
    def inst_blocks(self) -> tuple[Behavior, ...]:
        return tuple(self._inst_blocks)

    @property
    def conn_blocks(self) -> tuple[Behavior, ...]:
        return tuple(self._conn_blocks)

    @property
    def comb_blocks(self) -> tuple[Behavior, ...]:
        return tuple(self._comb_blocks)

    @property
    def seq_blocks(self) -> tuple[Behavior, ...]:
        return tuple(self._seq_blocks)

    @property
    def is_root(self) -> bool:
        if self._top is self:
            assert self._owner is None
            assert self._level == 0
            return True
        return False

    @property
    def is_assembled_module(self) -> bool:
        if self._obj.is_module:
            assert self._obj.assembled
            return True
        return False

    @property
    def is_assembled_package(self) -> bool:
        if self._obj.is_package:
            assert self._obj.assembled
            return True
        return False

    # Elements
    #
    def append_element(self, element: CircuitNode):
        """Append a sub-element node to the circuit."""
        assert self._top
        self._elements.append(element)
        element._owner = self
        element._level = self._level + 1
        element._full_name = f"{self._full_name}.{element._name}"
        element._top = self._top

    def remove_element(self, element: CircuitNode):
        """Remove a sub-element node from the circuit."""
        assert not element.elements
        self._elements.remove(element)
        element._owner = None
        element._level = 0
        element._full_name = element._name
        element._top = None

    def get_element(self, full_name: str) -> Optional[CircuitNode]:
        """Retrieve a sub-element node by its full name."""
        return self.__get_element(full_name.split("."))

    def __get_element(self, names: list[str]) -> Optional[CircuitNode]:
        if names[0] != self._name:
            return None
        if len(names) == 1:
            return self
        nodes = list(filter(lambda x: x._name == names[1], self._elements))
        if not nodes:
            return None
        assert len(nodes) == 1
        return nodes[0].__get_element(names[1:])

    # Iterator
    #
    def __iter__(self):
        return CircuitNodeBFSIterator(self)

    def iter_bfs(self):
        """Return breadth-first traversal iterator."""
        return CircuitNodeBFSIterator(self)

    def iter_dfs(self):
        """Return depth-first traversal iterator."""
        return CircuitNodeDFSIterator(self)

    def iter_postorder(self):
        """Return post-order traversal iterator (children first)."""
        return CircuitNodePostOrderIterator(self)

    # Hierarchy
    #
    def get_hierarchy_till(self, top_name: str) -> list[CircuitNode]:
        """Return the list of nodes from the current node up to the specified
        top node (inclusive).
        """
        assert "." not in top_name
        all_names = self._full_name.split(".")[::-1]
        try:
            idx = all_names.index(top_name)
        except ValueError:
            return []
        nodes = [self]
        for _ in range(idx):
            owner = nodes[-1]._owner
            assert owner
            nodes.append(owner)
        assert nodes[-1]._name == top_name
        return nodes[::-1]

    # Module
    #
    def register_submodule(self, inst: ModuleInst):
        """Register a module instance to the circuit."""
        assert isinstance(inst, ModuleInst)
        assert isinstance(inst.module_obj, RawModule)
        self._inst_blocks.append(Behavior.submodule(inst))

    def register_connection(self, conn: Connection):
        """Register a connection block to the circuit."""
        assert isinstance(conn, Connection)
        assert type(conn.func) is FunctionType
        self._conn_blocks.append(Behavior.connection(conn))

    def init_behavior_blocks(self):
        """Initialize behavioral blocks from the module object."""
        assert isinstance(self._obj, RawModule)
        blocks = self._obj.get_comb_blocks()
        self._comb_blocks = [Behavior.comb_block(f) for f in blocks]
        blocks = self._obj.get_seq_blocks()
        self._seq_blocks = [Behavior.seq_block(f) for f in blocks]

    def load_func_info(self, func: Callable) -> FuncCodeInfo:
        """Load and cache function information by the module class."""
        assert isinstance(self._obj, RawModule)
        return self._obj.load_func_info(func)

    def get_func_info_by_name(self, name: str) -> Optional[FuncCodeInfo]:
        """Get function information from the module class"""
        assert isinstance(self._obj, RawModule)
        return self._obj.get_func_info_by_name(name)

    def get_builder_frame_info(self, frame: inspect.FrameInfo) -> FuncCodeInfo:
        """Get function information of a stack frame from the module class"""
        assert isinstance(self._obj, RawModule)
        return self._obj.get_builder_frame_info(frame)

    def attach_ir_top(self, mlir_module):
        """Attach the top-level MLIR module to the circuit tree."""
        import circt.ir as IR

        assert isinstance(mlir_module, IR.Module)
        assert self._ir_top is None
        assert self.is_root
        self._ir_top = mlir_module
