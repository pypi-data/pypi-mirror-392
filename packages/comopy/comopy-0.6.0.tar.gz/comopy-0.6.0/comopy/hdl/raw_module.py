# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Base class for all HDL modules.
"""

from __future__ import annotations

import inspect
from itertools import chain
from typing import Any, Callable, Optional, Sequence

from comopy.utils import FuncCodeInfo, HDLAssemblyError

from .circuit_object import CircuitObject
from .signal import Input, Wire
from .tagged_class import TaggedClass, tagged_method

# Internal builder for module port connections
_hdl_internal_builder = "_connect_submodule_port"


# Decorators for tagged methods
#
def build(method: Callable) -> Callable:
    """Module methods that construct the circuit components."""
    return tagged_method(method, "build")


def comb(method: Callable) -> Callable:
    """Module methods that describe combinational logic."""
    return tagged_method(method, "comb")


def seq(method: Callable) -> Callable:
    """Module methods that describe sequential flip-flop logic."""
    return tagged_method(method, "seq")


class RawModule(TaggedClass, CircuitObject):
    """Base class for all HDL modules."""

    # Class attributes
    _tags: tuple[str, ...] = ("build", "comb", "seq")
    _auto_pos_edges: tuple[str, ...] = ()
    _auto_neg_edges: tuple[str, ...] = ()
    _auto_ports: tuple[str, ...] = ()
    _func_info: dict[str, FuncCodeInfo] = {}

    # Initialize class attributes
    def __init_subclass__(subclass):
        super().__init_subclass__()
        # Create caches for each subclass
        subclass._func_info = {}

    # Class methods
    #
    @classmethod
    def get_builders(cls) -> tuple[Callable, ...]:
        """Get all tagged methods for builders."""
        return cls.get_tagged_methods("build")

    @classmethod
    def get_builder_names(cls) -> Sequence[str]:
        """Get method names of all builders for searching stack frame."""
        return [f.__name__ for f in cls.get_builders()]

    @classmethod
    def get_comb_blocks(cls) -> tuple[Callable, ...]:
        """Get all tagged methods for combinational blocks."""
        return cls.get_tagged_methods("comb")

    @classmethod
    def get_seq_blocks(cls) -> tuple[Callable, ...]:
        """Get all tagged methods for sequential blocks."""
        return cls.get_tagged_methods("seq")

    @classmethod
    def load_func_info(cls, func: Callable) -> FuncCodeInfo:
        """Load and cache code information for a function."""
        assert callable(func)
        id = func.__qualname__
        info = cls._func_info.get(id, None)
        if not info:
            info = FuncCodeInfo(func)
            info.parse_ast()
            cls._func_info[id] = info
        return info

    @classmethod
    def get_func_info_by_name(cls, name: str) -> Optional[FuncCodeInfo]:
        """Get code information of a function."""
        return cls._func_info.get(name, None)

    @classmethod
    def get_builder_frame_info(cls, frame: inspect.FrameInfo) -> FuncCodeInfo:
        """Get function information of a stack frame."""
        # Check current bound builder first
        func_name = frame.function
        func_filename = frame.filename
        func_lineno = frame.frame.f_code.co_firstlineno
        builder = getattr(cls, func_name, None)
        assert callable(builder)
        info = cls.load_func_info(builder)
        if info.file_path == func_filename and info.lineno == func_lineno:
            return info
        # Search all builders in MRO
        # Cannot get the qualified name of a frame function in Python <3.11.
        # Python 3.11 introduces 'frame.f_code.co_qualname'.
        builder = None
        for func in reversed(cls.get_mro_tagged_methods("build")):
            if func.__name__ != func_name:
                continue
            cached = cls._func_info.get(func.__qualname__, None)
            if cached:
                filename = cached.file_path
                lineno = cached.lineno
            else:
                file = inspect.getsourcefile(func)
                assert file
                filename = file
                _, lineno = inspect.getsourcelines(func)
            if filename == func_filename and lineno == func_lineno:
                builder = func
                break
        assert callable(builder)
        return cls.load_func_info(builder)

    # Instance attributes
    _ports: list[CircuitObject]
    _port_conns: list[Any]  # Signal | auto port name, avoid circular import
    _ir: Any  # CIRCT IR hw.HWModuleOp
    _simulator: Any  # Simulator instance
    _translator: Any  # Translator instance
    _vsimulator: Any  # Verilator-based simulator instance

    # Initialize instance
    def __init__(self, *args, **kwargs):
        TaggedClass.__init__(self)
        CircuitObject.__init__(self)
        self._ports = []
        self._port_conns = []
        self._ir = None
        self._simulator = None
        self._translator = None
        self._vsimulator = None

    # CircuitObject
    #
    @property
    def is_module(self) -> bool:
        return True

    # Properties
    #
    @property
    def all_ports(self) -> Sequence[CircuitObject]:
        assert self.assembled
        return self._ports

    @property
    def port_conns(self) -> Sequence[Any]:
        assert self.assembled
        return self._port_conns

    @property
    def param_names(self) -> Sequence[str]:
        # TODO param
        return []

    @property
    def ir(self):
        return self._ir

    @property
    def simulator(self):
        return self._simulator

    @property
    def translator(self):
        return self._translator

    @property
    def vsimulator(self):
        return self._vsimulator

    # Tool attachments
    #
    def attach_ir(self, ir):
        from circt.dialects.hw import HWModuleOp

        assert isinstance(ir, HWModuleOp)
        assert self._ir is None
        self._ir = ir

    def attach_simulator(self, simulator):
        from comopy.simulator.base_simulator import BaseSimulator

        assert isinstance(simulator, BaseSimulator)
        assert self._simulator is None
        self._simulator = simulator

    def attach_translator(self, translator):
        from comopy.translator.base_translator import BaseTranslator

        assert isinstance(translator, BaseTranslator)
        assert self._translator is None
        self._translator = translator

    def attach_vsimulator(self, vsimulator):
        from comopy.verilator.vsimulator import VSimulator

        assert isinstance(vsimulator, VSimulator)
        assert self._vsimulator is None
        self._vsimulator = vsimulator

    # Assembling
    #
    def assemble(self):
        """Assemble the module by invoking all registered builder methods."""
        self.init_tagged_methods()
        self.__check_method_name_conflict()
        self.__check_auto_port_name_conflict()
        self.__build_auto_ports()
        builders = self.get_tagged_methods("build")
        for func in builders:
            func(self)
        self.__collect_ports()

    def __check_method_name_conflict(self):
        # Instantiate a RawModule to collect all class/instance attributes
        raw_module_names = set(dir(RawModule()))
        tagged_names = set()
        for tag in self._tags:
            for method in self.get_tagged_methods(tag):
                tagged_names.add(method.__name__)
        conflicts = raw_module_names & tagged_names
        if conflicts:
            cls_name = self.__class__.__name__
            conflict_names = ", ".join(sorted(conflicts))
            raise NameError(
                f"Tagged methods in {cls_name} cannot override "
                f"RawModule names: {conflict_names}"
            )

    def __check_auto_port_name_conflict(self):
        auto_pos_edges = set(self._auto_pos_edges)
        auto_neg_edges = set(self._auto_neg_edges)
        auto_ports = set(self._auto_ports)
        dup_names = auto_neg_edges & auto_pos_edges
        dup_names |= auto_ports & auto_pos_edges
        dup_names |= auto_ports & auto_neg_edges
        if dup_names:
            cls_name = self.__class__.__name__
            names = ", ".join(sorted(dup_names))
            raise NameError(
                f"Duplicated auto port names in module {cls_name}: {names}"
            )

    def __build_auto_ports(self):
        for name in self._auto_pos_edges:
            self.__setattr__(name, Input())
        for name in self._auto_neg_edges:
            self.__setattr__(name, Input())
        for name in self._auto_ports:
            self.__setattr__(name, Input())

    def __collect_ports(self):
        assert not self._ports
        assert not self._port_conns
        cls = self.__class__.__name__
        members = vars(self).values()
        self._ports = [
            p for p in members if isinstance(p, CircuitObject) and p.is_port
        ]
        port_names = [p.name for p in self._ports]
        n_ports = len(self._ports)
        conns = [None] * n_ports

        # Connect ports by order
        n_auto_ports = len(self._auto_pos_edges) + len(self._auto_neg_edges)
        n_auto_ports += len(self._auto_ports)
        if self._args:
            n = n_ports - n_auto_ports
            if len(self._args) > n:
                raise ValueError(
                    f"{cls}() expects {n} port arguments, "
                    f"got {len(self._args)}."
                )
            for i, arg in enumerate(self._args):
                # Check it in @= operator later.
                conns[i + n_auto_ports] = arg

        # Connect ports by name
        for name, conn in self._kwargs.items():
            if name not in port_names:
                raise ValueError(f"Invalid port name '{name}' in {cls}().")
            if self._args:
                raise ValueError(
                    f"{cls}() cannot mix ordered and named port connections."
                )
            idx = port_names.index(name)
            # Check it in @= operator later.
            conns[idx] = conn
        self._port_conns = conns

    # Submodule connection
    #
    def connect_submodule(self, submodule: RawModule):
        assert getattr(self, submodule.name, None) is submodule

        # Connect auto ports
        all_auto_ports = chain(
            self._auto_pos_edges, self._auto_neg_edges, self._auto_ports
        )
        for port_name in all_auto_ports:
            port = getattr(self, port_name, None)
            assert isinstance(port, Wire) and port.is_scalar_input
            submodule.__connect_auto_port(port)

        # Connect submodule ports
        for i, conn in enumerate(submodule._port_conns):
            if conn is None:
                continue
            port = submodule._ports[i]
            assert isinstance(port, CircuitObject)
            if port.is_input_port:
                self._connect_submodule_port(port, conn)
            elif port.is_output_port:
                self._connect_submodule_port(conn, port)
            else:
                assert port.is_inout_port
                # Only support in-out IOStruct
                self._connect_submodule_port(port, conn)
                self._connect_submodule_port(conn, port)

    def __connect_auto_port(self, port: Wire):
        port_name = port.name
        if not (
            port_name in self._auto_pos_edges
            or port_name in self._auto_neg_edges
            or port_name in self._auto_ports
        ):
            return
        for i, p in enumerate(self._ports):
            if p.name == port_name:
                assert isinstance(p, Wire) and p.is_scalar_input
                if self._port_conns[i] is not None:
                    raise HDLAssemblyError(
                        f"Port '{port_name}' has been auto-connected."
                    )
                self._port_conns[i] = port
                break

    # Internal builder for module port connections
    # '_hdl_internal_builder' saves the name of this builder function.
    def _connect_submodule_port(self, dst, src):
        dst @= src
