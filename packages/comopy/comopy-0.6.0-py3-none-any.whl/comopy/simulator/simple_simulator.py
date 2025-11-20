# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Simple simulator for executing all behavioral blocks within an HDL module.
"""

import comopy.hdl as HDL

from .base_simulator import BaseSimulator


class SimpleSimulator(BaseSimulator):
    """A simple simulator that executes all behavioral blocks in a module."""

    _module_node: HDL.CircuitNode
    _module: HDL.RawModule
    _evaluated: bool
    _in_port_bits: dict[str, int]  # port name -> saved value

    def __init__(self, module_node: HDL.CircuitNode):
        assert isinstance(module_node, HDL.CircuitNode)
        assert module_node.is_assembled_module
        assert isinstance(module_node.obj, HDL.RawModule)
        self._module_node = module_node
        self._module = module_node.obj
        self._evaluated = False
        self._in_port_bits = {}

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
        assert self._module.simulating
        assert not self._evaluated, "UNIMPLEMENTED"  # stop -> start
        assert not self._module_node.inst_blocks  # Not support submodules
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
        active_seq_blocks = self.__active_seq_blocks(active_inputs)

        # Execute all connection and behavioral blocks in the module
        # NOTE: This simple implementation executes all blocks in their
        # definition order without dependency analysis or scheduling.
        # It works correctly only for:
        # 1. Modules with a single type of blocks (@comb or @seq, not mixed)
        # 2. When the source code order matches the evaluation dependency order
        for seq_block in active_seq_blocks:
            assert callable(seq_block.func)
            seq_block.func(self._module)
        for seq_block in active_seq_blocks:
            self.__update_seq_block(seq_block)

        for comb_block in self._module_node.comb_blocks:
            assert callable(comb_block.func)
            comb_block.func(self._module)

        for conn_block in self._module_node.conn_blocks:
            assert callable(conn_block.func)
            conn_block.func()

        self.__save_ports(self._in_port_bits)

        # This simple simulator ignores triggered signals
        return set()

    def __triggered_ports(self, saved_ports: dict[str, int]) -> set[str]:
        triggered = set()
        for name in saved_ports:
            port = getattr(self._module, name, None)
            assert isinstance(port, HDL.Wire) and port.is_port
            if port.data_bits.unsigned != saved_ports[name]:
                triggered.add(name)
        return triggered

    def __active_seq_blocks(
        self, active_inputs: set[str]
    ) -> list[HDL.Behavior]:
        active_blocks = []
        for block in self._module_node.seq_blocks:
            assert isinstance(block, HDL.Behavior)
            assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
            for port in block.edges.pos_edges:
                if port in active_inputs and self._in_port_bits[port] == 0:
                    active_blocks.append(block)
                    break
            else:
                for port in block.edges.neg_edges:
                    if port in active_inputs and self._in_port_bits[port] == 1:
                        active_blocks.append(block)
                        break
        return active_blocks

    def __update_seq_block(self, block: HDL.Behavior):
        for name in block.deps.writes:
            signal = getattr(self._module, name, None)
            assert isinstance(signal, HDL.Signal)
            signal.flip()

    def __save_ports(self, saved_ports: dict[str, int]):
        for name in saved_ports:
            port = getattr(self._module, name, None)
            assert isinstance(port, HDL.Wire) and port.is_port
            saved_ports[name] = port.data_bits.unsigned

    def tick(self):
        """Run one clock cycle."""
        assert self._module_node.is_root
        if not isinstance(self._module, HDL.Module):
            raise RuntimeError("tick() requires a Module with clock")
        self._module.clk /= 0
        self.evaluate()
        self._module.clk /= 1
        self.evaluate()
