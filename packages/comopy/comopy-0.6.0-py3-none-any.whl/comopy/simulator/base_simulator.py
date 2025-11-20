# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Abstract base class defining the interface for all simulators.
"""

from abc import ABC, abstractmethod

from comopy.hdl import RawModule


class BaseSimulator(ABC):
    """Base class for all simulators."""

    # Simulation interfaces
    #
    @property
    @abstractmethod
    def module(self) -> RawModule:
        """Get the associated RawModule object."""

    @abstractmethod
    def start(self):
        """Start simulation."""

    @abstractmethod
    def _init_all_module_ports(self):
        """Initialize all module ports. Internal use only for start()."""

    @abstractmethod
    def stop(self):
        """Stop simulation."""

    @abstractmethod
    def evaluate(self) -> set[str]:
        """Evaluate the circuit and return the set of triggered signals."""

    @abstractmethod
    def tick(self):
        """Run one clock cycle."""
