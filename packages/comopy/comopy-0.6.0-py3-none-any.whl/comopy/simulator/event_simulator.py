# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

""" Event-driven simulator that runs the Python code of an HDL module.
"""

from itertools import chain
from typing import Optional, Sequence

import comopy.hdl as HDL

from .base_simulator import BaseSimulator

DEBUG_EVAL = False
# DEBUG_EVAL = True


class EventSimulator(BaseSimulator):
    """Event-driven simulator that runs the Python code of a module.

    Evaluates the module using a zero-delay simulation model.
    Inputs should be set on inactive clock edges. Any input triggered on
    an active clock edge will be counted into the sampling of flip-flops in
    this zero-delay model, which is impractical in real hardware.
    """

    _module_node: HDL.CircuitNode
    _module: HDL.RawModule
    _evaluated: bool
    _all_edges: set[str]
    _in_port_bits: dict[str, int]  # port name -> saved value
    _out_port_bits: dict[str, int]  # port name -> saved value
    _nba_updates: list[HDL.Behavior]

    def __init__(self, module_node: HDL.CircuitNode):
        assert isinstance(module_node, HDL.CircuitNode)
        assert module_node.is_assembled_module
        assert isinstance(module_node.obj, HDL.RawModule)
        self._module_node = module_node
        self._module = module_node.obj
        self._evaluated = False
        self._all_edges = self.__get_all_edges()
        self._in_port_bits = {}
        self._out_port_bits = {}
        self._nba_updates = []

    def __get_all_edges(self) -> set[str]:
        all_edges = set()
        for block in self._module_node.seq_blocks:
            assert isinstance(block, HDL.Behavior)
            assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
            all_edges.update(block.edges.pos_edges)
            all_edges.update(block.edges.neg_edges)
        return all_edges

    @property
    def module(self) -> HDL.RawModule:
        return self._module

    def start(self):
        """Start the simulation."""
        assert self._module_node.is_root
        assert not self._module.simulating
        for node in self._module_node:
            node.obj.simulating = True
        self._init_all_module_ports()

    def _init_all_module_ports(self):
        """Initialize all module ports. Internal use only for start()."""
        from .scheduled_simulator import ScheduledSimulator

        assert self._module.simulating
        assert not self._evaluated, "UNIMPLEMENTED"  # stop -> start
        for inst_block in self._module_node.inst_blocks:
            assert isinstance(inst_block, HDL.Behavior)
            assert isinstance(inst_block.inst, HDL.ModuleInst)
            submodule = inst_block.inst.module_obj
            assert isinstance(submodule, HDL.RawModule)
            simulator = submodule.simulator
            assert isinstance(simulator, (EventSimulator, ScheduledSimulator))
            simulator._init_all_module_ports()
        self._evaluated = True
        self.__init_ports()

    def __init_ports(self):
        assert not self._in_port_bits
        for port in self._module.all_ports:
            assert isinstance(port, HDL.Wire) and port.is_port
            assert not port.is_inout_port, "UNIMPLEMENTED"
            if port.is_input_port:
                self._in_port_bits[port.name] = port.data_bits.unsigned
            if port.is_output_port:
                self._out_port_bits[port.name] = port.data_bits.unsigned

    def stop(self):
        """Stop the simulation."""
        assert self._module_node.is_root
        assert self._module.simulating
        for node in self._module_node:
            node.obj.simulating = False

    def evaluate(self) -> set[str]:
        """Evaluate the circuit and return the set of triggered signals."""
        assert self._module.simulating
        assert not self._nba_updates
        self.__save_ports(self._out_port_bits)
        active = self.__triggered_ports(self._in_port_bits)
        active_edges, active_seq_blocks = self.__active_seqs(active)

        # Data signals must hold while edge triggered
        if active_edges:
            non_edge_active = active - self._all_edges
            if non_edge_active:
                edges = ", ".join(f"'{s}'" for s in sorted(active_edges))
                signals = ", ".join(f"'{s}'" for s in sorted(non_edge_active))
                raise RuntimeError(
                    f"Data hold violation in {self._module_node.full_name}: "
                    f"{signals} changed while {edges} triggered."
                )

        # Evaluate constant blocks (no reads).
        m = self._module_node
        non_seq_blocks = chain(m.conn_blocks, m.comb_blocks, m.inst_blocks)
        for block in non_seq_blocks:
            if not block.deps.reads:
                active |= self.__eval_non_seq(block)

        # Evaluate all blocks and submodules triggered by active signals.
        # Evaluate RHS for @seq blocks only once per cycle (edge).
        # A submodule may be evaluated multiple times, but the edges
        # for its @seq blocks are triggered only once per cycle.
        while active:
            triggered = set()
            non_seq_blocks = chain(m.conn_blocks, m.comb_blocks, m.inst_blocks)
            for block in non_seq_blocks:
                if block.deps.reads & active:
                    triggered |= self.__eval_non_seq(block)
            for block in active_seq_blocks:
                if block.deps.reads & active:
                    if block not in self._nba_updates:
                        self.__eval_seq(block)
                        self._nba_updates.append(block)
            if DEBUG_EVAL:
                print(f"  {active} => {triggered}")
            active = triggered

            # If all signals are stable, update non-blocking assignments (NBAs)
            # for @seq blocks. The new values of the flip-flops may trigger
            # further evaluation of combinational logic.
            if not active:
                active |= self.__nba_update(self._nba_updates)
                if DEBUG_EVAL and self._nba_updates:
                    print(f"NBA => {active}")
                self._nba_updates.clear()
                active_seq_blocks.clear()

        if DEBUG_EVAL:
            print(f"----Module evaluated: {self._module_node.full_name}----")
        self.__save_ports(self._in_port_bits)
        return self.__triggered_ports(self._out_port_bits)

    def __save_ports(self, saved_ports: dict[str, int]):
        for name in saved_ports:
            port = getattr(self._module, name, None)
            assert isinstance(port, HDL.Wire) and port.is_port
            saved_ports[name] = port.data_bits.unsigned

    def __triggered_ports(self, saved_ports: dict[str, int]) -> set[str]:
        triggered = set()
        for name in saved_ports:
            port = getattr(self._module, name, None)
            assert isinstance(port, HDL.Wire) and port.is_port
            if port.data_bits.unsigned != saved_ports[name]:
                triggered.add(name)
        return triggered

    def __active_seqs(
        self, active_inputs: set[str]
    ) -> tuple[set[str], list[HDL.Behavior]]:
        active_edges = set()
        active_blocks = {}  # Deduplicate blocks by ID
        for block in self._module_node.seq_blocks:
            assert isinstance(block, HDL.Behavior)
            assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK

            for port in block.edges.pos_edges:
                if port in active_inputs and self._in_port_bits[port] == 0:
                    active_edges.add(port)
                    if block.id not in active_blocks:
                        active_blocks[block.id] = block

            for port in block.edges.neg_edges:
                if port in active_inputs and self._in_port_bits[port] == 1:
                    active_edges.add(port)
                    if block.id not in active_blocks:
                        active_blocks[block.id] = block

        return active_edges, list(active_blocks.values())

    def __eval_non_seq(self, block: HDL.Behavior) -> set[str]:
        if DEBUG_EVAL:
            print(f"  {block.id} : {block.deps}")
        writes = block.deps.writes
        self.__save_signals(writes)
        if block.kind == HDL.Behavior.Kind.COMB_BLOCK:
            assert callable(block.func)
            block.func(self._module)
        elif block.kind == HDL.Behavior.Kind.CONNECTION:
            assert callable(block.func)
            block.func()
        else:
            assert block.kind == HDL.Behavior.Kind.MODULE_INST
            assert isinstance(block.inst, HDL.ModuleInst)
            submodule = block.inst.module_obj
            assert isinstance(submodule, HDL.RawModule)
            assert isinstance(submodule.simulator, BaseSimulator)
            submodule.simulator.evaluate()
        return self.__triggered_signals(writes)

    def __save_signals(self, sig_names: set[str]):
        for name in sig_names:
            signal = self.__get_signal(name)
            signal.save()

    def __triggered_signals(self, sig_names: set[str]) -> set[str]:
        triggered = set()
        for name in sig_names:
            signal = self.__get_signal(name)
            if signal.changed():
                triggered.add(name)
        return triggered

    def __get_signal(self, name: str) -> HDL.Signal | HDL.SignalArray:
        module_obj: Optional[HDL.RawModule] = self._module
        if "." in name:
            inst_name, name = name.split(".", 1)
            assert "." not in name
            module_obj = getattr(self._module, inst_name, None)
            assert isinstance(module_obj, HDL.RawModule)
        signal = getattr(module_obj, name, None)
        assert isinstance(signal, (HDL.Signal, HDL.SignalArray))
        return signal

    def __eval_seq(self, block: HDL.Behavior):
        if DEBUG_EVAL:
            print(f"  {block.id} : {block.deps}")
        assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
        assert callable(block.func)
        block.func(self._module)

    def __nba_update(
        self, active_seq_blocks: Sequence[HDL.Behavior]
    ) -> set[str]:
        triggered = set()
        for block in active_seq_blocks:
            assert isinstance(block, HDL.Behavior)
            assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
            writes = block.deps.writes
            for name in writes:
                signal = getattr(self._module, name, None)
                assert isinstance(signal, (HDL.Signal, HDL.SignalArray))
                signal.flip()
            if DEBUG_EVAL:
                print(f"  {block.id} : {block.deps} (flipped)")
            triggered |= writes
        return triggered

    def tick(self):
        """Run one clock cycle."""
        assert self._module_node.is_root
        if not isinstance(self._module, HDL.Module):
            raise RuntimeError("tick() requires a Module with clock")
        self._module.clk /= 0
        self.evaluate()
        self._module.clk /= 1
        self.evaluate()
