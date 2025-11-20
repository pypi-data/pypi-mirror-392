# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Simulator that statically schedules all behavioral blocks within an HDL module.
"""

import graphlib
from itertools import chain
from typing import Sequence

import comopy.hdl as HDL

from .base_simulator import BaseSimulator

DEBUG_EVAL = False
# DEBUG_EVAL = True


class ScheduledSimulator(BaseSimulator):
    """Simulator that statically schedules all behavioral blocks in a module.

    If there is no cycle (circular dependency) among behavioral blocks,
    each block is evaluated only once per simulation step, with no need for
    multiple iterations. This static scheduling approach applies to any module
    without feedback paths or circular dependencies.
    """

    _module_node: HDL.CircuitNode
    _module: HDL.RawModule
    _evaluated: bool
    _all_edges: set[str]
    _in_port_bits: dict[str, int]  # port name -> saved value
    _scheduled_blocks: list[HDL.Behavior]

    def __init__(self, module_node: HDL.CircuitNode):
        assert isinstance(module_node, HDL.CircuitNode)
        assert module_node.is_assembled_module
        assert isinstance(module_node.obj, HDL.RawModule)
        self._module_node = module_node
        self._module = module_node.obj
        self._evaluated = False
        self._all_edges = self.__get_all_edges()
        self._in_port_bits = {}
        self._scheduled_blocks = self.__schedule_blocks()

    def __get_all_edges(self) -> set[str]:
        all_edges = set()
        for block in self._module_node.seq_blocks:
            assert isinstance(block, HDL.Behavior)
            assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
            all_edges.update(block.edges.pos_edges)
            all_edges.update(block.edges.neg_edges)
        return all_edges

    def __schedule_blocks(self) -> list[HDL.Behavior]:
        """Statically schedule all behavioral blocks in the module."""
        # Map block IDs to behavioral blocks
        node = self._module_node
        n_blocks = len(node.inst_blocks)
        n_blocks += len(node.conn_blocks)
        n_blocks += len(node.comb_blocks)
        blocks = chain(node.inst_blocks, node.conn_blocks, node.comb_blocks)
        id_to_block = {b.id: b for b in blocks}
        assert len(id_to_block) == n_blocks  # All block IDs are unique

        # Build dependency graph and perform topological sorting
        dep_graph = self.__build_dependency_graph()
        try:
            sorter = graphlib.TopologicalSorter(dep_graph)
            sorted_block_ids = list(sorter.static_order())
        except graphlib.CycleError as e:
            cycle = " -> ".join(e.args[1])
            raise ValueError(f"Cycle detected in static scheduling: {cycle}")

        # Convert sorted IDs back to behavioral block objects
        scheduled = []
        for block_id in sorted_block_ids:
            assert block_id in id_to_block
            scheduled.append(id_to_block[block_id])

        return scheduled

    def __build_dependency_graph(self) -> dict[str, set[str]]:
        # All inputs and registers (NBA outputs)
        node = self._module_node
        inputs_and_regs = set()
        for port in self._module.all_ports:
            assert isinstance(port, HDL.Wire) and port.is_port
            assert not port.is_inout_port, "UNIMPLEMENTED"
            if port.is_input_port:
                inputs_and_regs.add(port.name)
        for seq_block in node.seq_blocks:
            for signal in seq_block.deps.writes:
                inputs_and_regs.add(signal)

        # Dependency graph: reader block -> {predecessors (writers)}
        dep_graph: dict[str, set[str]] = {}

        # All signal writers: signal -> {all writers}
        signal_writers: dict[str, set[str]] = {}

        # Add combinational logic writers (comb blocks+connections+submodules)
        blocks = chain(node.conn_blocks, node.comb_blocks, node.inst_blocks)
        for block in blocks:
            for signal in block.deps.writes:
                if signal not in signal_writers:
                    signal_writers[signal] = set()
                signal_writers[signal].add(block.id)

        # Find dependencies for combinational blocks based on read signals
        blocks = chain(node.conn_blocks, node.comb_blocks, node.inst_blocks)
        for block in blocks:
            deps = set()
            for signal in block.deps.reads:
                if signal in signal_writers:
                    for writer_id in signal_writers[signal]:
                        deps.add(writer_id)
                else:
                    assert signal in inputs_and_regs
            dep_graph[block.id] = deps

        return dep_graph

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
        from .event_simulator import EventSimulator

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

    def stop(self):
        """Stop the simulation."""
        assert self._module_node.is_root
        assert self._module.simulating
        for node in self._module_node:
            node.obj.simulating = False

    def evaluate(self) -> set[str]:
        """Evaluate the circuit and return the set of triggered signals."""
        assert self._module.simulating
        active_inputs = self.__triggered_ports(self._in_port_bits)

        # Propagate active inputs through connections first
        for block in self._scheduled_blocks:
            if block.kind != HDL.Behavior.Kind.CONNECTION:
                continue
            if active_inputs & block.deps.reads:
                if DEBUG_EVAL:
                    print(f"  {block.id} : {block.deps}")
                assert callable(block.func)
                block.func()

        # Evaluate sequential blocks if any edge triggered
        active_edges, active_seq_blocks = self.__active_seqs(active_inputs)
        if active_edges:
            # Data signals must hold while edge triggered
            non_edge_inputs = active_inputs - self._all_edges
            if non_edge_inputs:
                edges = ", ".join(f"'{s}'" for s in sorted(active_edges))
                signals = ", ".join(f"'{s}'" for s in sorted(non_edge_inputs))
                raise RuntimeError(
                    f"Data hold violation in {self._module_node.full_name}: "
                    f"{signals} changed while {edges} triggered."
                )
            for block in active_seq_blocks:
                if DEBUG_EVAL:
                    print(f"  {block.id} : {block.deps}")
                assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
                assert callable(block.func)
                block.func(self._module)
            for inst_block in self._module_node.inst_blocks:
                self.__eval_inst(inst_block)
            self.__nba_update(active_seq_blocks)
        elif active_inputs:
            # Update submodules for possible edges
            for inst_block in self._module_node.inst_blocks:
                self.__eval_inst(inst_block)

        # Evaluate all combinational blocks in scheduled order
        for block in self._scheduled_blocks:
            if DEBUG_EVAL:
                print(f"  {block.id} : {block.deps}")
            if block.kind == HDL.Behavior.Kind.CONNECTION:
                assert callable(block.func)
                block.func()
            elif block.kind == HDL.Behavior.Kind.MODULE_INST:
                self.__eval_inst(block)
            else:
                assert callable(block.func)
                block.func(self._module)

        if DEBUG_EVAL:
            print(f"----Module evaluated: {self._module_node.full_name}----")
        self.__save_ports(self._in_port_bits)
        return set()

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

    def __eval_inst(self, inst_block: HDL.Behavior):
        assert isinstance(inst_block, HDL.Behavior)
        assert inst_block.kind == HDL.Behavior.Kind.MODULE_INST
        assert isinstance(inst_block.inst, HDL.ModuleInst)
        submodule = inst_block.inst.module_obj
        assert isinstance(submodule, HDL.RawModule)
        submodule.simulator.evaluate()

    def __nba_update(self, active_seq_blocks: Sequence[HDL.Behavior]):
        for block in active_seq_blocks:
            assert isinstance(block, HDL.Behavior)
            assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
            for name in block.deps.writes:
                signal = getattr(self._module, name, None)
                assert isinstance(signal, (HDL.Signal, HDL.SignalArray))
                signal.flip()
            if DEBUG_EVAL:
                print(f"  {block.id} : {block.deps} (flipped)")

    def tick(self):
        """Run one clock cycle."""
        assert self._module_node.is_root
        if not isinstance(self._module, HDL.Module):
            raise RuntimeError("tick() requires a Module with clock")
        self._module.clk /= 0
        self.evaluate()
        self._module.clk /= 1
        self.evaluate()
