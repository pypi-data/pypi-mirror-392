# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Setup simulators for all HDL modules in a circuit hierarchy.
"""

from comopy.config import get_comopy_context
from comopy.hdl import CircuitNode, RawModule
from comopy.utils import BasePass

from .base_simulator import BaseSimulator
from .event_simulator import EventSimulator
from .scheduled_simulator import ScheduledSimulator
from .simple_simulator import SimpleSimulator


class SetupSimulator(BasePass):
    """A pass to setup simulators for all modules in a circuit tree."""

    _sim_class: type[BaseSimulator]
    _auto_type: bool = False

    def __init__(self):
        super().__init__()
        self._auto_type = False
        config = get_comopy_context().sim_config
        match config.simulator_type:
            case "auto":
                self._auto_type = True
                self._sim_class = ScheduledSimulator
            case "event":
                self._sim_class = EventSimulator
            case "scheduled":
                self._sim_class = ScheduledSimulator
            case "simple":
                self._sim_class = SimpleSimulator
            case _:
                raise ValueError(
                    f"Unknown simulator type: '{config.simulator_type}'."
                    "\n- Supported types: 'auto', 'scheduled', 'simple'."
                )

    def __call__(self, tree: CircuitNode) -> CircuitNode:
        assert isinstance(tree, CircuitNode)
        assert tree.is_root and tree.is_assembled_module
        top_module = tree.obj
        assert isinstance(top_module, RawModule)
        if top_module.simulator:
            raise RuntimeError(
                f"Simulator for '{top_module.name}' has already been set up."
            )

        for node in tree:
            if node.is_assembled_module:
                module = node.obj
                assert isinstance(module, RawModule)
                assert module.simulator is None
                try:
                    sim = self._sim_class(node)  # type: ignore[call-arg]
                    module.attach_simulator(sim)
                except ValueError:
                    # Cycle detected in static scheduling
                    if not self._auto_type:
                        raise
                    sim = EventSimulator(node)
                    module.attach_simulator(sim)

        return tree
