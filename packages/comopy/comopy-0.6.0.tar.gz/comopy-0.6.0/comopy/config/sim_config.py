# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Simulator stage configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulatorConfig:

    simulator_type: str = "auto"

    @staticmethod
    def auto() -> SimulatorConfig:
        return SimulatorConfig(simulator_type="auto")

    @staticmethod
    def event() -> SimulatorConfig:
        return SimulatorConfig(simulator_type="event")

    @staticmethod
    def scheduled() -> SimulatorConfig:
        return SimulatorConfig(simulator_type="scheduled")

    @staticmethod
    def simple() -> SimulatorConfig:
        return SimulatorConfig(simulator_type="simple")
